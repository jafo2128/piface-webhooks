"""
tests/test_notifiers.py

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

import sys
from datetime import datetime

from piface_webhooks.notifiers import Pushover, Webhook, Gmail

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call
else:
    from unittest.mock import patch, call


# patch base
pbm = 'piface_webhooks.notifiers'


class TestPushoverInit(object):

    def test_init(self):
        cls = Pushover('mykey')
        assert cls.api_token == 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up'
        assert cls.user_key == 'mykey'
        assert cls.title == 'piface input change'
        assert cls.url is None
        assert cls.priority == 0
        assert cls.sound is None

    def test_init_options(self):
        cls = Pushover('mykey', title='foo', url='myurl', priority=2,
                       sound='mysound')
        assert cls.api_token == 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up'
        assert cls.user_key == 'mykey'
        assert cls.title == 'foo'
        assert cls.url == 'myurl'
        assert cls.priority == 2
        assert cls.sound == 'mysound'


class TestPushover(object):

    def setup(self):
        self.cls = Pushover('mykey')

    def test_send(self):
        with patch('%s.Pushover._pushover_send' % pbm) as mock_p_send:
            self.cls.send(datetime(2015, 2, 13, 1, 2, 3, 123456),
                          2, 0, 'pin2', 'pin2state0')
        assert mock_p_send.mock_calls == [
            call('pin2 (2) changed to pin2state0 (0)',
                 datetime(2015, 2, 13, 1, 2, 3, 123456))
        ]

    def test_pushover_send(self):
        expected = {
            'user': 'mykey',
            'timestamp': 1423807323,
            'title': 'piface input change',
            'token': 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up',
            'message': 'mymsg',
            'priority': 0
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.logger' % pbm) as mock_logger:
                type(mock_post.return_value).status_code = 200
                mock_post.return_value.json.return_value = {'status': 1}
                self.cls._pushover_send('mymsg',
                                        datetime(2015, 2, 13, 1, 2, 3, 123456))
        assert mock_post.mock_calls == [
            call('https://api.pushover.net/1/messages.json', data=expected),
            call().json()
        ]
        assert mock_logger.mock_calls == [
            call.debug("Sending POST to Pushover; data: %s", expected)
        ]

    def test_pushover_send_with_opts(self):
        self.cls.priority = 2
        self.cls.sound = 'falling'
        self.cls.url = 'myurl'
        expected = {
            'user': 'mykey',
            'timestamp': 1423807323,
            'title': 'piface input change',
            'token': 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up',
            'message': 'mymsg',
            'priority': 2,
            'sound': 'falling',
            'url': 'myurl'
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.logger' % pbm) as mock_logger:
                type(mock_post.return_value).status_code = 200
                mock_post.return_value.json.return_value = {'status': 1}
                self.cls._pushover_send('mymsg',
                                        datetime(2015, 2, 13, 1, 2, 3, 123456))
        assert mock_post.mock_calls == [
            call('https://api.pushover.net/1/messages.json', data=expected),
            call().json()
        ]
        assert mock_logger.mock_calls == [
            call.debug("Sending POST to Pushover; data: %s", expected)
        ]

    def test_pushover_send_error(self):
        expected = {
            'user': 'mykey',
            'timestamp': 1423807323,
            'title': 'piface input change',
            'token': 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up',
            'message': 'mymsg',
            'priority': 0
        }
        resp_json = {
            'status': 0, 'user': 'invalid',
            'errors': ['user identifier is invalid']
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.logger' % pbm) as mock_logger:
                type(mock_post.return_value).status_code = 401
                mock_post.return_value.json.return_value = resp_json
                self.cls._pushover_send('mymsg',
                                        datetime(2015, 2, 13, 1, 2, 3, 123456))
        assert mock_post.mock_calls == [
            call('https://api.pushover.net/1/messages.json', data=expected),
            call().json()
        ]
        assert mock_logger.mock_calls == [
            call.debug("Sending POST to Pushover; data: %s", expected),
            call.critical("POST to Pushover returned %s", 401),
            call.critical("POST to Pushover returned bad status: %s", resp_json)
        ]

    def test_pushover_cant_decode_json(self):
        expected = {
            'user': 'mykey',
            'timestamp': 1423807323,
            'title': 'piface input change',
            'token': 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up',
            'message': 'mymsg',
            'priority': 0
        }

        def se_exc():
            raise Exception("foo")

        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.logger' % pbm) as mock_logger:
                type(mock_post.return_value).status_code = 200
                mock_post.return_value.json.side_effect = se_exc
                self.cls._pushover_send('mymsg',
                                        datetime(2015, 2, 13, 1, 2, 3, 123456))
        assert mock_post.mock_calls == [
            call('https://api.pushover.net/1/messages.json', data=expected),
            call().json()
        ]
        assert mock_logger.mock_calls == [
            call.debug("Sending POST to Pushover; data: %s", expected),
            call.critical("POST to Pushover - response could not be decoded")
        ]

    def test_pushover_no_status(self):
        expected = {
            'user': 'mykey',
            'timestamp': 1423807323,
            'title': 'piface input change',
            'token': 'aB5D3uoGZuVQg4QMJMm8817sJFn7Up',
            'message': 'mymsg',
            'priority': 0
        }
        resp_json = {
            'foo': 'bar'
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.logger' % pbm) as mock_logger:
                type(mock_post.return_value).status_code = 200
                mock_post.return_value.json.return_value = resp_json
                self.cls._pushover_send('mymsg',
                                        datetime(2015, 2, 13, 1, 2, 3, 123456))
        assert mock_post.mock_calls == [
            call('https://api.pushover.net/1/messages.json', data=expected),
            call().json()
        ]
        assert mock_logger.mock_calls == [
            call.debug("Sending POST to Pushover; data: %s", expected),
            call.critical("POST to Pushover - response lacks status element")
        ]


class TestWebhook(object):

    def setup(self):
        self.cls = Webhook('myurl')

    def test_init(self):
        cls = Webhook('myurl')
        assert cls.url == 'myurl'
        assert cls.use_get is False

    def test_init_get(self):
        cls = Webhook('myurl', use_get=True)
        assert cls.url == 'myurl'
        assert cls.use_get is True

    def test_send(self):
        dt = datetime(2015, 2, 13, 1, 2, 3, 123456)
        expected = {
            'timestamp': 1423807323,
            'datetime_iso8601': '2015-02-13T01:02:03',
            'pin_num': 2,
            'pin_name': 'pin2',
            'state': 0,
            'state_name': 'state0name',
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.requests.get' % pbm) as mock_get:
                with patch('%s.logger' % pbm) as mock_logger:
                    type(mock_post.return_value).status_code = 200
                    type(mock_get.return_value).status_code = 200
                    self.cls.send(dt, 2, 0, 'pin2', 'state0name')
        assert mock_get.mock_calls == []
        assert mock_post.mock_calls == [call('myurl', data=expected)]
        assert mock_logger.mock_calls == [
            call.debug('POSTing to %s: %s', 'myurl', expected)
        ]

    def test_send_error(self):
        dt = datetime(2015, 2, 13, 1, 2, 3, 123456)
        expected = {
            'timestamp': 1423807323,
            'datetime_iso8601': '2015-02-13T01:02:03',
            'pin_num': 2,
            'pin_name': 'pin2',
            'state': 0,
            'state_name': 'state0name',
        }
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.requests.get' % pbm) as mock_get:
                with patch('%s.logger' % pbm) as mock_logger:
                    type(mock_post.return_value).status_code = 401
                    type(mock_get.return_value).status_code = 401
                    self.cls.send(dt, 2, 0, 'pin2', 'state0name')
        assert mock_get.mock_calls == []
        assert mock_post.mock_calls == [call('myurl', data=expected)]
        assert mock_logger.mock_calls == [
            call.debug('POSTing to %s: %s', 'myurl', expected),
            call.critical("Request to %s returned status code %s", 'myurl', 401)
        ]

    def test_send_get(self):
        dt = datetime(2015, 2, 13, 1, 2, 3, 123456)
        expected = {
            'timestamp': 1423807323,
            'datetime_iso8601': '2015-02-13T01:02:03',
            'pin_num': 2,
            'pin_name': 'pin2',
            'state': 0,
            'state_name': 'state0name',
        }
        self.cls.use_get = True
        with patch('%s.requests.post' % pbm) as mock_post:
            with patch('%s.requests.get' % pbm) as mock_get:
                with patch('%s.logger' % pbm) as mock_logger:
                    type(mock_post.return_value).status_code = 200
                    type(mock_get.return_value).status_code = 200
                    self.cls.send(dt, 2, 0, 'pin2', 'state0name')
        assert mock_post.mock_calls == []
        assert mock_get.mock_calls == [call('myurl', data=expected)]
        assert mock_logger.mock_calls == [
            call.debug('GETing %s with: %s', 'myurl', expected)
        ]


class TestGmail(object):

    def setup(self):
        self.cls = Gmail('to@a.com', 'from@a.com', 'myuser', 'mypass')

    def test_init(self):
        cls = Gmail('t', 'f', 'u', 'p')
        assert cls.to_addr == 't'
        assert cls.from_addr == 'f'
        assert cls.username == 'u'
        assert cls.password == 'p'

    def test_send(self):
        dt = datetime(2015, 2, 13, 1, 2, 3, 123456)
        with patch('%s.Gmail._send_gmail' % pbm) as mock_send:
            self.cls.send(dt, 1, 0, 'pin1', 'state0')
        assert mock_send.mock_calls == [
            call(
                'pin1 (1) changed to state0 (0) at 2015-02-13T01:02:03',
                "2015-02-13T01:02:03\npin1 (1) changed state to state0 (0)"
            )
        ]

    def test_send_gmail(self):
        msg = 'Content-Type: text/plain; charset="us-ascii"\nMIME-Version: ' \
              '1.0\nContent-Transfer-Encoding: 7bit\nSubject: mysubj\nFrom: ' \
              'from@a.com\nTo: to@a.com\n\nmy\nbody'
        with patch('%s.smtplib.SMTP' % pbm, autospec=True) as mock_smtp:
            self.cls._send_gmail('mysubj', "my\nbody")
        assert mock_smtp.mock_calls == [
            call('smtp.gmail.com:587'),
            call().starttls(),
            call().login('myuser', 'mypass'),
            call().sendmail('from@a.com', ['to@a.com'], msg),
            call().quit()
        ]
