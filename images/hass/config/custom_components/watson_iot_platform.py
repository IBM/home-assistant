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


"""
A component which allows you to send data to the IBM Watson IoT Platform.
"""

import logging
import queue
import threading
import time

import voluptuous as vol

from homeassistant.const import (
    CONF_DOMAINS, CONF_ENTITIES, CONF_EXCLUDE, CONF_INCLUDE,
    CONF_TOKEN, CONF_TYPE, EVENT_STATE_CHANGED, EVENT_HOMEASSISTANT_STOP,
    STATE_UNAVAILABLE, STATE_UNKNOWN)
from homeassistant.helpers import state as state_helper
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['ibmiotf==0.3.4']

_LOGGER = logging.getLogger(__name__)

CONF_ORG = 'organization'
CONF_ID = 'id'

DOMAIN = 'watson_iot_platform'

RETRY_DELAY = 20

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(vol.Schema({
        vol.Required(CONF_ORG): cv.string,
        vol.Required(CONF_TYPE): cv.string,
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Optional(CONF_EXCLUDE, default={}): vol.Schema({
            vol.Optional(CONF_ENTITIES, default=[]): cv.entity_ids,
            vol.Optional(CONF_DOMAINS, default=[]):
                vol.All(cv.ensure_list, [cv.string])
        }),
        vol.Optional(CONF_INCLUDE, default={}): vol.Schema({
            vol.Optional(CONF_ENTITIES, default=[]): cv.entity_ids,
            vol.Optional(CONF_DOMAINS, default=[]):
                vol.All(cv.ensure_list, [cv.string])
        }),
    })),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Watson IoT Platform component."""
    from ibmiotf import gateway

    conf = config[DOMAIN]

    include = conf.get(CONF_INCLUDE, {})
    exclude = conf.get(CONF_EXCLUDE, {})
    whitelist_e = set(include.get(CONF_ENTITIES, []))
    whitelist_d = set(include.get(CONF_DOMAINS, []))
    blacklist_e = set(exclude.get(CONF_ENTITIES, []))
    blacklist_d = set(exclude.get(CONF_DOMAINS, []))

    client_args = {
        'org': conf.get(CONF_ORG),
        'type': conf.get(CONF_TYPE),
        'id': conf.get(CONF_ID),
        'auth-method': 'token',
        'auth-token': conf.get(CONF_TOKEN),
    }
    watson_gateway = gateway.Client(client_args)

    def event_to_json(event):
        """Add an event to the outgoing list."""
        state = event.data.get('new_state')
        if state is None or state.state in (
                STATE_UNKNOWN, '', STATE_UNAVAILABLE) or \
                state.entity_id in blacklist_e or state.domain in blacklist_d:
            return

        try:
            if (whitelist_e and state.entity_id not in whitelist_e) or \
                    (whitelist_d and state.domain not in whitelist_d):
                return

            _include_state = _include_value = False

            _state_as_value = float(state.state)
            _include_value = True
        except ValueError:
            try:
                _state_as_value = float(state_helper.state_as_number(state))
                _include_state = _include_value = True
            except ValueError:
                _include_state = True

        out_event = {
            'tags': {
                'domain': state.domain,
                'entity_id': state.object_id,
            },
            'time': event.time_fired.isoformat(),
            'fields': {}
        }
        if _include_state:
            out_event['fields']['state'] = state.state
        if _include_value:
            out_event['fields']['value'] = _state_as_value

        for key, value in state.attributes.items():
            if key != 'unit_of_measurement':
                # If the key is already in fields
                if key in out_event['fields']:
                    key = key + "_"
                # For each value we try to cast it as float
                # But if we can not do it we store the value
                # as string
                try:
                    out_event['fields'][key] = float(value)
                except (ValueError, TypeError):
                    out_event['fields'][key] = str(value)

        return out_event

    instance = hass.data[DOMAIN] = WatsonIOTThread(
        hass, watson_gateway, event_to_json)
    instance.start()

    def shutdown(event):
        """Shut down the thread."""
        instance.queue.put(None)
        instance.join()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, shutdown)

    return True


class WatsonIOTThread(threading.Thread):
    """A threaded event handler class."""

    def __init__(self, hass, gateway, event_to_json):
        """Initialize the listener."""
        threading.Thread.__init__(self, name='WatsonIOT')
        self.queue = queue.Queue()
        self.gateway = gateway
        self.gateway.connect()
        self.event_to_json = event_to_json
        self.max_tries = 3
        self.write_errors = 0
        self.shutdown = False
        hass.bus.listen(EVENT_STATE_CHANGED, self._event_listener)

    def _event_listener(self, event):
        """Listen for new messages on the bus and queue them for Watson IOT."""
        item = (time.monotonic(), event)
        self.queue.put(item)

    def get_events_json(self):
        """Return an event formatted for writing."""
        events = []

        try:
            item = self.queue.get()

            if item is None:
                self.shutdown = True
            else:
                event_json = self.event_to_json(item[1])
                if event_json:
                    events.append(event_json)

        except queue.Empty:
            pass

        return events

    def write_to_watson(self, events):
        """Write preprocessed events to watson."""
        import ibmiotf

        for event in events:
            for retry in range(self.max_tries + 1):
                try:
                    for field in event['fields']:
                        value = event['fields'][field]
                        device_success = self.gateway.publishDeviceEvent(
                            event['tags']['domain'],
                            event['tags']['entity_id'],
                            field, 'json', value)
                    if not device_success:
                        _LOGGER.error(
                            "Failed to publish message to watson iot")
                        continue
                    break
                except (ibmiotf.MissingMessageEncoderException, IOError):
                    if retry < self.max_tries:
                        time.sleep(RETRY_DELAY)
                    else:
                        _LOGGER.exception(
                            "Failed to publish message to watson iot")

    def run(self):
        """Process incoming events."""
        while not self.shutdown:
            event = self.get_events_json()
            if event:
                self.write_to_watson(event)
            self.queue.task_done()

    def block_till_done(self):
        """Block till all events processed."""
        self.queue.join()
