#!/bin/bash
python3 -m venv --without-pip venv
source venv/bin/activate
curl https://bootstrap.pypa.io/pip/3.6/get-pip.py | python
deactivate
