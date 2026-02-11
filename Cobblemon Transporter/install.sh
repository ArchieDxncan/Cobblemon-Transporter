#!/bin/bash
sudo apt install python3-tk -y
python3 -m venv venv
source venv/bin/activate
pip install nbtlib requests pillow tkinterdnd2