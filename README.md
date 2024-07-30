# SSR PCAP Watcher

## Background

PCAP files are often very useful for troubleshooting. However, it can often be very difficult to collect all the needed information due to the default log rotation properties of the 128T application. This script seeks to aid in that by monitoring specified interface and service capture files and, upon rotation by the 128T application, copy the first complete file rotation to an alternate directory (default /tmp). Additionally, when Ctrl-C is pressed to end the script, it will copy the latest (non-rotated) capture files to this direectory as well in order to have as complete a picture as possible.

## Install

This one liner can be used on the SSR Linux prompt to copy the script from Github and setup a python3 virtual environment as well as installing the additionally needed package into the virtual environment.

```sh
curl https://raw.githubusercontent.com/laneshields/ssr-pcap-watcher/main/setup.sh | bash
```

## Usage

From the directory where this was installed:

```sh
./watch_pcap -i <LAN interface> -i <WAN interface> -s <service/session capture service-name> [-o <output directory>]
```

The options `-i` and `-s` can be specified multiple times to capture more than one interface and/or session capture. The default output directory is `/tmp`.

## Additional Comments
* **WARNING** This script makes no attempt to prevent you from shooting yourself in the foot by filling up the disk drive, please be careful
* After transferring pcaps off box, it is useful to use Wireshark's `mergecap` command to combine the files. Be sure to use the `-a` option in order to concatenate the files and **NOT** merge by timestamp. The pcaps should be ordered in such a way that they are automatically ordered by capture time and Wireshark's attempt to merge by time will likely result in missed packets from the end of one capture file if the start of a new capture file has the same timestamp. Example:
`mergecap -a -w 128T_ge-0-0-merged.pcap 128T_ge-0-0.2024*`
