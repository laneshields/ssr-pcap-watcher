#!venv/bin/python

import argparse
import pathlib
import pyinotify
import shutil
import sys

from datetime import datetime

LOGDIR = pathlib.Path("/var") / "log" / "128technology"
IF_CAPTURE_FILE_FORMAT = "128T_{}.pcap"
SERVICE_CAPTURE_FILE_FORMAT = "128T_service_{}.pcap"

class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, wm, outdir, callback):
        self.wm = wm
        self.outdir = outdir
        self.callback = callback

    def process_IN_CREATE_SELF(self, event):
        print(f"create: {event}")

    def process_IN_MOVE_SELF(self, event):
        unrotated_path = get_unrotated(pathlib.Path(event.pathname))
        my_wd = self.wm.get_wd(event.pathname)
        self.wm.rm_watch(my_wd)
        self.callback(self.outdir, unrotated_path, event.pathname)
        self.wm.add_watch(str(unrotated_path), pyinotify.IN_MOVE_SELF)

def get_basename(path):
    return path.name[: -len(''.join(path.suffixes))]

def get_unrotated(path):
    return (path.parent / get_basename(path)).with_suffix(path.suffix)

def file_rotated_callback(outdir, monitored_file, rotated_filename):
    dest_file = outdir / f"{monitored_file.stem}.{datetime.now().strftime('%Y%m%d%H%M%S%f')}{monitored_file.suffix}"
    print(f"Copying {rotated_filename} to {dest_file}")
    shutil.copy(rotated_filename, str(dest_file))


def main(args):
    wm = pyinotify.WatchManager()
    outdir = pathlib.Path(args.out_dir)
    try:
        assert outdir.is_dir()
    except AssertionError:
        print(f"Error: Specified output directory ({outdir}) does not exist or is not a directory")
        exit(1)
    event_handler = EventHandler(wm, outdir, file_rotated_callback)
    notifier = pyinotify.Notifier(wm, event_handler)
    wm.add_watch(str(LOGDIR), pyinotify.ALL_EVENTS)
    try:
        if args.interface:
            for interface in args.interface:
                wm.add_watch(
                    str(LOGDIR / IF_CAPTURE_FILE_FORMAT.format(interface)),
                    pyinotify.IN_MOVE_SELF | pyinotify.IN_CREATE | pyinotify.IN_DELETE,
                    quiet=False
                )
        if args.service:
            for service in args.service:
                wm.add_watch(
                    str(LOGDIR / SERVICE_CAPTURE_FILE_FORMAT.format(service)),
                    pyinotify.IN_MOVE_SELF | pyinotify.IN_CREATE | pyinotify.IN_DELETE,
                    quiet=False
                )
    except pyinotify.WatchManagerError as err:
            print(f"error: {err}")
            print(f"{pathlib.Path(__file__).name} must watch existing files, please send some traffic and try again or check the option values passed")
            exit(1)
    print(f"Watching files for rotation, press Ctrl-C when your test has completed")
    notifier.loop()
    print("\nloop broken, copying current latest capture files")
    for _, watch in wm.watches.items():
        fp = pathlib.Path(watch.path)
        if fp.is_file():
            file_rotated_callback(outdir, fp, fp)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
           WARNING: This script takes no action to avoid using up available disk space!!! Please be careful when using!!!


           This script attempts to prevent loss of SSR capture file data due to file rotation. It watches SSR pcaps in real time 
           as they are rotated by the SSR application and, upon rotation, copies files to an alternate directory. Additionaly
           after pressing Ctrl-C to end this process it will copy the last non-rotated capture file to attempt to have a complete
           picture.

           Multiple switches for -i or -s can be passed to watch multiple interfaces or service capture files.
        """,
        epilog="Note: When combining captures with wireshark's mergecap, be sure to use the -a command or else packets at the end of individual files could be lost"
    )
    parser.add_argument('-i', '--interface', action='append', help='Interface capture to follow')
    parser.add_argument('-s', '--service', action='append', help='Service capture to follow')
    parser.add_argument('-o', '--out-dir', default='/tmp', help='Output directory to copy captures to')
    args = parser.parse_args()

    if args.interface is None and args.service is None:
        parser.error("At least one of --interfaces or --service required")

    main(args)
