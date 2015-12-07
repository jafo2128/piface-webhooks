"""
tests/test_listener.py

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

import argparse
import pytest
import sys
import logging

from piface_webhooks.listener import Listener, console_entry_point
from piface_webhooks.version import VERSION

from pifacedigitalio import PiFaceDigital, IODIR_ON, IODIR_OFF
from pifacecommon.interrupts import InterruptEvent

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, mock_open
else:
    from unittest.mock import patch, call, Mock, mock_open


# patch base
pbm = 'piface_webhooks.listener'
pb = '%s.Listener' % pbm


class TestEntryPoint(object):

    with patch(pb) as mock_listener:
        console_entry_point()
    assert mock_listener.mock_calls == [
        call(),
        call().console_entry_point()
    ]


class TestListener(object):

    def setup(self):
        self.mock_chip = Mock(spec_set=PiFaceDigital)
        self.pin0 = Mock()
        self.pin1 = Mock()
        self.pin2 = Mock()
        self.pin3 = Mock()
        type(self.mock_chip).output_pins = [
            self.pin0, self.pin1, self.pin2, self.pin3
        ]
        with patch('%s.PiFaceDigital' % pbm) as mock_pfd:
            mock_pfd.return_value = self.mock_chip
            self.cls = Listener()
        self.cls.chip = self.mock_chip

    def test_module_entry_point(self):
        with patch(pb) as mock_listener:
            console_entry_point()
        assert mock_listener.mock_calls == [
            call(),
            call().console_entry_point(),
        ]

    def test_parse_args(self):
        argv = ['-V']
        res = self.cls.parse_args(argv)
        assert isinstance(res, argparse.Namespace)
        assert res.version is True

    def test_parse_args_parser(self):
        argv = ['-V']
        desc = 'Listen for PiFace input changes and queue them to disk'
        with patch('%s.argparse.ArgumentParser' % pbm,
                   spec_set=argparse.ArgumentParser) as mock_parser:
                self.cls.parse_args(argv)
        assert mock_parser.mock_calls == [
            call(description=desc),
            call().add_argument('-v', '--verbose', dest='verbose',
                                action='count',
                                default=0,
                                help='verbose output. specify twice '
                                'for debug-level output.'),
            call().add_argument('-V', '--version', dest='version',
                                action='store_true',
                                default=False,
                                help='print version number and exit.'),
            call().parse_args(argv),
        ]

    def test_entry_point_version(self, capsys):
        argv = ['piface-webhooks', '-V']
        with patch.object(sys, 'argv', argv):
            with patch('%s.run' % pb) as mock_run:
                with pytest.raises(SystemExit) as excinfo:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == "pyface-webhooks %s " \
            "<https://github.com/jantman/piface_webhooks>\n" % VERSION
        assert err == ''
        assert excinfo.value.code == 0
        assert mock_run.mock_calls == []

    def test_entry_verbose(self, capsys):
        argv = ['piface-webhooks', '-v']
        with patch.object(sys, 'argv', argv):
            with patch('%s.logger.setLevel' % pbm) as mock_set_level:
                with patch('%s.run' % pb) as mock_run:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''
        assert mock_set_level.mock_calls == [call(logging.INFO)]
        assert mock_run.mock_calls == [call()]

    def test_entry_debug(self, capsys):
        argv = ['piface-webhooks', '-vv']
        with patch.object(sys, 'argv', argv):
            with patch('%s.logger.setLevel' % pbm) as mock_set_level:
                with patch('%s.run' % pb) as mock_run:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''
        assert mock_set_level.mock_calls == [call(logging.DEBUG)]
        assert mock_run.mock_calls == [call()]

    def test_entry_none(self, capsys):
        argv = ['piface-webhooks']
        with patch.object(sys, 'argv', argv):
            with patch('%s.logger.setLevel' % pbm) as mock_set_level:
                with patch('%s.run' % pb) as mock_run:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''
        assert mock_set_level.mock_calls == []
        assert mock_run.mock_calls == [call()]

    def test_run(self):
        with patch('%s.logger' % pbm) as mock_logger:
            with patch('%s.InputEventListener' % pbm) as mock_listener:
                with patch('%s.PiFaceDigital' % pbm) as mock_io:
                    self.cls.run()
        assert mock_logger.mock_calls == [
            call.debug("initializing chip"),
            call.debug("chip initialized"),
            call.debug('creating InputEventListener'),
            call.debug('registering callback for %s ON', 0),
            call.debug('registering callback for %s OFF', 0),
            call.debug('registering callback for %s ON', 1),
            call.debug('registering callback for %s OFF', 1),
            call.debug('registering callback for %s ON', 2),
            call.debug('registering callback for %s OFF', 2),
            call.debug('registering callback for %s ON', 3),
            call.debug('registering callback for %s OFF', 3),
            call.debug('activating listener'),
            call.warning('Listener exited')
        ]
        assert mock_listener.mock_calls == [
            call(chip=self.cls.chip),
            call().register(0, IODIR_ON, self.cls.handle_input_on),
            call().register(0, IODIR_OFF, self.cls.handle_input_off),
            call().register(1, IODIR_ON, self.cls.handle_input_on),
            call().register(1, IODIR_OFF, self.cls.handle_input_off),
            call().register(2, IODIR_ON, self.cls.handle_input_on),
            call().register(2, IODIR_OFF, self.cls.handle_input_off),
            call().register(3, IODIR_ON, self.cls.handle_input_on),
            call().register(3, IODIR_OFF, self.cls.handle_input_off),
            call().activate()
        ]
        assert mock_io.mock_calls == [call()]
        assert self.cls.chip == mock_io.return_value

    def test_handle_input_on(self):
        mock_evt = Mock(spec_set=InterruptEvent)
        type(mock_evt).pin_num = 3
        type(mock_evt).timestamp = 1234.5678

        with patch('%s.handle_change' % pb) as mock_handle:
            with patch('%s.logger' % pbm) as mock_logger:
                self.cls.handle_input_on(mock_evt)
        assert mock_logger.mock_calls == [
            call.info("Received ON event for pin %s", 3),
            call.debug("Setting output %s on", 3),
            call.debug("Set output %s on", 3)
        ]
        assert mock_handle.mock_calls == [call(3, True, 1234.5678)]
        assert self.mock_chip.mock_calls == []
        assert self.pin0.mock_calls == []
        assert self.pin1.mock_calls == []
        assert self.pin2.mock_calls == []
        assert self.pin3.mock_calls == [call.turn_on()]

    def test_handle_input_off(self):
        mock_evt = Mock(spec_set=InterruptEvent)
        type(mock_evt).pin_num = 1
        type(mock_evt).timestamp = 1234.5678

        with patch('%s.handle_change' % pb) as mock_handle:
            with patch('%s.logger' % pbm) as mock_logger:
                self.cls.handle_input_off(mock_evt)
        assert mock_logger.mock_calls == [
            call.info("Received ON event for pin %s", 1),
            call.debug("Setting output %s off", 1),
            call.debug("Set output %s off", 1)
        ]
        assert mock_handle.mock_calls == [call(1, False, 1234.5678)]
        assert self.mock_chip.mock_calls == []
        assert self.pin0.mock_calls == []
        assert self.pin1.mock_calls == [call.turn_off()]
        assert self.pin2.mock_calls == []
        assert self.pin3.mock_calls == []

    def test_handle_change_on(self):
        fpath = '/foo/bar/pinevent_123.4567_2_on'
        with patch('%s.settings.QUEUE_PATH' % pbm, '/foo/bar'):
            with patch('%s.logger' % pbm) as mock_logger:
                with patch('%s.open' % pbm,
                           mock_open(read_data='')) as mock_opn:
                    with patch('%s.os.utime' % pbm) as mock_utime:
                        self.cls.handle_change(2, True, 123.4567)
        assert mock_logger.mock_calls == [
            call.debug("Created event file: %s", fpath)
        ]
        assert mock_opn.mock_calls == [
            call(fpath, 'a'),
            call().__enter__(),
            call().__exit__(None, None, None)
        ]
        assert mock_utime.mock_calls == [
            call(fpath, None)
        ]

    def test_handle_change_off(self):
        fpath = '/foo/bar/pinevent_123.4567_2_off'
        with patch('%s.settings.QUEUE_PATH' % pbm, '/foo/bar'):
            with patch('%s.logger' % pbm) as mock_logger:
                with patch('%s.open' % pbm,
                           mock_open(read_data='')) as mock_opn:
                    with patch('%s.os.utime' % pbm) as mock_utime:
                        self.cls.handle_change(2, False, 123.4567)
        assert mock_logger.mock_calls == [
            call.debug("Created event file: %s", fpath)
        ]
        assert mock_opn.mock_calls == [
            call(fpath, 'a'),
            call().__enter__(),
            call().__exit__(None, None, None)
        ]
        assert mock_utime.mock_calls == [
            call(fpath, None)
        ]
