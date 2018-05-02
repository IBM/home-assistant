#!/bin/sh

if ! command -v python3 &>/dev/null; then
    echo "python 3 is required to run home assistant"
    exit 1
fi

echo "Creating venv at $PWD/homeassistant-venv"

python3 -m venv homeassistant-venv

echo "Installing Home Assistant in venv"
echo ""

homeassistant-venv/bin/pip install -U homeassistant &> venv.log

echo "Home Assistant is now running, use ctrl+c or sending SIGTERM to stop it."
echo "If you want to start it again just run:"
echo ""
echo "./homeassistant-venv/bin/hass --config config"
echo ""
echo " from the root of the repo"

./homeassistant-venv/bin/hass --config config --open-ui &> home-assistant.log
