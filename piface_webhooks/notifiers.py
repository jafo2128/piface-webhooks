"""
notifiers.py

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

import logging
import time
import requests

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


class Pushover(object):

    def __init__(self, user_key, title='piface input change',
                 url=None, priority=0, sound=None):
        """
        For the priority and sound options, see:
        <https://pushover.net/api>
        """
        self.api_token = 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up'
        self.user_key = user_key
        self.title = title
        self.url = url
        self.priority = priority
        self.sound = sound

    def send(self, evt_datetime, pin_num, state, pin_name, state_name):
        """
        Send a notification to the specified user via pushover.

        :param evt_datetime: the time the input changed state
        :type evt_datetime: datetime.datetime
        :param pin_num: the pin number that changed
        :type pin_num: int
        :param state: the pin's new state (0==off, 1==on)
        :type state: int
        :param pin_name: pin name from the settings module
        :type pin_name: str
        :param state_name: state name from the settings module
        :type state_name: str
        """
        msg = '%s (%s) changed to %s (%s)' % (pin_name, pin_num,
                                              state_name, state)
        self._pushover_send(msg, evt_datetime)

    def _pushover_send(self, msg, evt_datetime):
        """
        Internal method to actually send the pushover message.

        :param msg: the message to send
        :type msg: str
        :param evt_datetime: the time the input changed state
        :type evt_datetime: datetime.datetime
        """
        data = {
            'token': self.api_token,
            'user': self.user_key,
            'message': msg,
            'title': self.title,
            'timestamp': int(time.mktime(evt_datetime.timetuple())),
            'priority': self.priority,
        }
        if self.url is not None:
            data['url'] = self.url
        if self.sound is not None:
            data['sound'] = self.sound
        logger.debug("Sending POST to Pushover; data: %s", data)
        r = requests.post('https://api.pushover.net/1/messages.json', data=data)
        if r.status_code != 200:
            logger.critical("POST to Pushover returned %s", r.status_code)
        if r.json['status'] != 1:
            logger.critical("POST to Pushover returned bad status: %s", r.json)
