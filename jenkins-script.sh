#! /usr/bin/env bash

if [ ! -d .venv ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
else
    source .venv/bin/activate
fi
python3 cla_script.py
