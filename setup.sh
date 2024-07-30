#!/bin/bash -x
echo "Pulling script from github"
curl -o watch_pcap https://raw.githubusercontent.com/laneshields/ssr-pcap-watcher/main/watch_pcap.py &> /dev/null
chmod +x watch_pcap &> /dev/null
echo "Creating python virtual environment..."
python3 -m venv --without-pip venv &> /dev/null
source venv/bin/activate &> /dev/null
echo "Installing pip and needed packages..."
curl https://bootstrap.pypa.io/pip/3.6/get-pip.py | python &> /dev/null
pip install pyinotify &> /dev/null
deactivate &> /dev/null
echo "Done. Use \"./watch_pcap -h\" for instructions"
