"""
tests/test_config.py

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

from piface_webhooks.config import Config

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock
else:
    from unittest.mock import patch, call, Mock


# patch base
pbm = 'piface_webhooks.config'
pb = '%s.Config' % pbm


class Container(object):
    """container class"""

    def __init__(self):
        pass


class TestInitConfig(object):

    def test_init(self):
        with patch('%s._load_settings' % pb) as mock_load:
            with patch('%s._set_defaults' % pb) as mock_defaults:
                Config()
        assert mock_load.mock_calls == [call()]
        assert mock_defaults.mock_calls == [call()]


class TestConfig(object):

    def setup(self):
        with patch('%s._load_settings' % pb):
            with patch('%s._set_defaults' % pb):
                self.cls = Config()

    def test_load_settings(self):
        mock_settings = Container()
        mock_settings.FOO = 1
        mock_settings.BAR = 2

        self.cls.FOO = 0

        env = {'foo': 'bar'}
        with patch('%s.os.environ' % pbm, env):
            with patch('%s._load_module' % pb) as mock_load:
                with patch('%s.logger' % pbm) as mock_logger:
                    mock_load.return_value = mock_settings
                    self.cls._load_settings()
        assert mock_logger.mock_calls == [
            call.debug("Loading settings from %s", 'piface_webhooks.settings')
        ]
        assert mock_load.mock_calls == [call('piface_webhooks.settings')]
        assert self.cls.FOO == 1
        assert self.cls.BAR == 2

    def test_load_settings_env_var(self):
        mock_settings = Container()
        mock_settings.FOO = 1
        mock_settings.BAR = 2

        self.cls.FOO = 0

        env = {
            'foo': 'bar',
            'PIFACE_WEBHOOKS_SETTINGS_MODULE': 'foo.bar',
        }
        with patch('%s.os.environ' % pbm, env):
            with patch('%s._load_module' % pb) as mock_load:
                with patch('%s.logger' % pbm) as mock_logger:
                    mock_load.return_value = mock_settings
                    self.cls._load_settings()
        assert mock_logger.mock_calls == [
            call.debug("Loading settings from %s", 'foo.bar')
        ]
        assert mock_load.mock_calls == [call('foo.bar')]
        assert self.cls.FOO == 1
        assert self.cls.BAR == 2

    def test_load_settings_no_settings(self):
        self.cls.FOO = 0

        env = {'foo': 'bar'}
        with patch('%s.os.environ' % pbm, env):
            with patch('%s._load_module' % pb) as mock_load:
                with patch('%s.logger' % pbm) as mock_logger:
                    mock_load.return_value = None
                    self.cls._load_settings()
        assert mock_logger.mock_calls == [
            call.debug("Loading settings from %s", 'piface_webhooks.settings'),
            call.error('Settings module %s could not be loaded; using default '
                       'settings!', 'piface_webhooks.settings')
        ]
        assert mock_load.mock_calls == [call('piface_webhooks.settings')]
        assert self.cls.FOO == 0

    def test_load_module(self):
        mock_mod = Mock()
        with patch('%s.importlib.import_module' % pbm) as mock_load:
            mock_load.return_value = mock_mod
            res = self.cls._load_module('foo')
        assert res == mock_mod
        assert mock_load.mock_calls == [call('foo')]

    def test_load_module_exception(self):
        def se_load(m):
            raise Exception("foo")

        with patch('%s.importlib.import_module' % pbm) as mock_load:
            mock_load.side_effect = se_load
            res = self.cls._load_module('foo')
        assert res is None
        assert mock_load.mock_calls == [call('foo')]

    def test_set_defaults(self):
        self.cls._set_defaults()
        assert self.cls.QUEUE_PATH == '/var/spool/piface-webhooks'
        assert self.cls.NO_LEDS is False
        assert self.cls.INVERT_LED is False
        assert self.cls.PINS == [
            {'name': 'Pin 0', 'states': ['off', 'on']},
            {'name': 'Pin 1', 'states': ['off', 'on']},
            {'name': 'Pin 2', 'states': ['off', 'on']},
            {'name': 'Pin 3', 'states': ['off', 'on']},
        ]
        assert self.cls.CALLBACKS == []
