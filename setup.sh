#!/bin/bash
# Copyright 2018 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if ! command -v python3 &>/dev/null; then
    echo "python 3 is required to run home assistant"
    exit 1
fi

echo "Creating venv at $PWD/homeassistant-venv"

python3 -m venv homeassistant-venv &> venv.log

echo "Installing Home Assistant in venv"
echo ""

./homeassistant-venv/bin/python3 -m pip install -U wheel &>> venv.log
./homeassistant-venv/bin/python3 -m pip install -U homeassistant &>> venv.log

echo "Home Assistant is now running, use ctrl+c or sending SIGTERM to stop it."
echo "If you want to start it again just run:"
echo ""
echo "./homeassistant-venv/bin/hass --config images/hass/config"
echo ""
echo " from the root of the repo"

./homeassistant-venv/bin/hass --config ./images/hass/config --open-ui &> home-assistant.log
