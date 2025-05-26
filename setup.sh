#!/bin/bash
echo "Setup CAN MUX pentru Raspberry Pi 5"
sudo apt update
sudo apt install -y python3-pip python3-venv i2c-tools
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Setup complet!"