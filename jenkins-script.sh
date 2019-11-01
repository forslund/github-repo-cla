#! /usr/bin/env bash


# Example script for running on Jenkins or other CI triggered on PR

if [ ! -d .venv ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
else
    source .venv/bin/activate
fi


# Run for all PR's against the dev branch on the repo MycroftAI/mycroft-core
python3 cla_script.py -b dev MycroftAI/mycroft-core
