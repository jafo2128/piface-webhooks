"""
settings.py

piface-webhooks configuration

The latest version of this package is available at:
<https://github.com/jantman/piface_webhooks>

################################################################################
Copyright 2015 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of piface_webhooks.

    piface_webhooks is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    piface_webhooks is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with piface_webhooks.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/piface_webhooks> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

# path on disk used to store the queue files; this directory must exist
QUEUE_PATH = '/var/spool/piface-webhooks'

###########################
# input pin configuration #
###########################
# Note that on the PiFace, output pins 0 and 1 have relays attached;
# this program will light the output pin LEDs, which means that it
# will trigger the relays for pins 0 and 1 unless the jumpers are
# changed.

PINS = [
    # pin 0
    {
        # a name to give the pin in messages
        'name': 'Pin 0',
        # human-readable descriptions of the states, for use in the messages
        'states': [
            # state 0 - off
            'off state text',
            # state 1 - on
            'on state text',
        ],
    },
    # pin 1
    {
        # a name to give the pin in messages
        'name': 'Pin 1',
        # human-readable descriptions of the states, for use in the messages
        'states': [
            # state 0 - off
            'off state text',
            # state 1 - on
            'on state text',
        ],
    },
    # pin 2
    {
        # a name to give the pin in messages
        'name': 'Pin 2',
        # human-readable descriptions of the states, for use in the messages
        'states': [
            # state 0 - off
            'off state text',
            # state 1 - on
            'on state text',
        ],
    },
    # pin 3
    {
        # a name to give the pin in messages
        'name': 'Pin 3',
        # human-readable descriptions of the states, for use in the messages
        'states': [
            # state 0 - off
            'off state text',
            # state 1 - on
            'on state text',
        ],
    },
]

###############################################
# Callback/notification/webhook configuration #
###############################################
# You can use the builtin classes for this, or define your own
# either here, or (ideally) anywhere that can be imported.
# The CALLBACKS list is a list of callables, each of which will
# be called with arguments as follows:
# - event datetime (datetime)
# - pin number (int)
# - new pin state/value (int, 0 or 1)
# - pin name (str)
# - pin state text/description (str)

push = Pushover('my_user_key')

CALLBACKS = [push.send]
