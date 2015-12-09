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
import smtplib
from email.mime.text import MIMEText

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

        This is the callback function.

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
        try:
            j = r.json()
        except:
            logger.critical("POST to Pushover - response could not be decoded")
            return
        if 'status' not in j:
            logger.critical("POST to Pushover - response lacks status element")
            return
        if j['status'] != 1:
            logger.critical("POST to Pushover returned bad status: %s", j)


class Webhook(object):
    """
    Sends a webhook to the specified URL. Parameters are as follows:

    timestamp - integer Unix timestamp for the event
    datetime_iso8601 - string iso8601 time of the event ('%Y-%m-%dT%H:%m:%s%z')
    pin_num - integer pin number
    pin_name - string pin name
    state - integer state
    state_name - string state name
    """

    def __init__(self, url, use_get=False):
        """
        Sends a webhook to the URL. Will send a POST unless use_get is True.
        """
        self.url = url
        self.use_get = use_get

    def send(self, evt_datetime, pin_num, state, pin_name, state_name):
        """
        Sends the webhook.

        This is the callback function.

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
        data = {
            'timestamp': int(time.mktime(evt_datetime.timetuple())),
            'datetime_iso8601': evt_datetime.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'pin_num': pin_num,
            'pin_name': pin_name,
            'state': state,
            'state_name': state_name
        }
        if self.use_get:
            logger.debug("GETing %s with: %s", self.url, data)
            res = requests.get(self.url, data=data)
        else:
            logger.debug("POSTing to %s: %s", self.url, data)
            res = requests.post(self.url, data=data)
        if res.status_code != 200:
            logger.critical("Request to %s returned status code %s",
                            self.url, res.status_code)


class Gmail(object):
    """
    Sends a notification via GMail.
    """

    def __init__(self, to_addr, from_addr, username, password):
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.username = username
        self.password = password

    def send(self, evt_datetime, pin_num, state, pin_name, state_name):
        """
        Sends the email.

        This is the callback function.

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
        subj = '%s (%s) changed to %s (%s) at %s' % (
            pin_name, pin_num, state_name, state,
            evt_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
        )
        msg = "%s\n%s (%s) changed state to %s (%s)" % (
            evt_datetime.strftime('%Y-%m-%dT%H:%M:%S%z'),
            pin_name, pin_num, state_name, state
        )
        self._send_gmail(subj, msg)

    def _send_gmail(self, subject, body):
        """Send email using GMail"""
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.from_addr
        msg['To'] = self.to_addr
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(self.username, self.password)
        s.sendmail(self.from_addr, [self.to_addr], msg.as_string())
        s.quit()
