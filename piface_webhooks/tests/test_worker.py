"""
tests/test_worker.py

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
from datetime import datetime

from piface_webhooks.worker import Worker, console_entry_point
from piface_webhooks.version import VERSION

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
pbm = 'piface_webhooks.worker'
pb = '%s.Worker' % pbm


class TestEntryPoint(object):

    def test_entry_point(self):
        with patch(pb) as mock_worker:
            console_entry_point()
        assert mock_worker.mock_calls == [
            call(),
            call().console_entry_point()
        ]


class TestInit(object):

    def test_init(self):
        with patch('%s.Config' % pbm) as mock_config:
            cls = Worker()
        assert mock_config.mock_calls == [call()]
        assert cls.config == mock_config.return_value
        assert cls.process_events is True


class TestWorker(object):

    def setup(self):
        with patch('%s.Config' % pbm) as mock_config:
            self.cls = Worker()
        self.config = mock_config.return_value

    def test_parse_args(self):
        argv = ['-V']
        res = self.cls.parse_args(argv)
        assert isinstance(res, argparse.Namespace)
        assert res.version is True

    def test_parse_args_parser(self):
        argv = ['-V']
        desc = 'PiFace input change event queue processor/worker'
        with patch('%s.argparse.ArgumentParser' % pbm,
                   spec_set=argparse.ArgumentParser) as mock_parser:
                self.cls.parse_args(argv)
        assert mock_parser.mock_calls == [
            call(description=desc),
            call().add_argument('-w', '--no-process', dest='process_events',
                                action='store_false', default=True,
                                help='do not process events, just log what '
                                'would be done (note this will cause events to '
                                'pile up on disk)'),
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
        argv = ['piface-worker', '-V']
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
        argv = ['piface-worker', '-v']
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
        argv = ['piface-worker', '-vv']
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
        argv = ['piface-worker']
        with patch.object(sys, 'argv', argv):
            with patch('%s.logger.setLevel' % pbm) as mock_set_level:
                with patch('%s.run' % pb) as mock_run:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''
        assert mock_set_level.mock_calls == []
        assert mock_run.mock_calls == [call()]
        assert self.cls.process_events is True

    def test_entry_no_write(self, capsys):
        argv = ['piface-worker', '--no-process']
        with patch.object(sys, 'argv', argv):
            with patch('%s.logger.setLevel' % pbm) as mock_set_level:
                with patch('%s.run' % pb) as mock_run:
                    self.cls.console_entry_point()
        out, err = capsys.readouterr()
        assert out == ''
        assert err == ''
        assert mock_set_level.mock_calls == []
        assert mock_run.mock_calls == [call()]
        assert self.cls.process_events is False

    def test_run(self):
        with patch('%s._alwaystrue' % pb) as mock_true:
            with patch('%s.handle_files' % pb) as mock_handle:
                with patch('%s.logger' % pbm) as mock_logger:
                    mock_true.side_effect = [True, True, False]
                    self.cls.run()
        assert mock_true.mock_calls == [call(), call(), call()]
        assert mock_handle.mock_calls == [call(), call()]
        assert mock_logger.mock_calls == [
            call.info("Beginning file handling loop")
        ]

    def test_alwaystrue(self):
        assert self.cls._alwaystrue() is True

    def test_handle_files(self):
        flist = [
            'foobar',
            'pinevent_1420863332.123456_pin2_state1',
            'pinevent_csds_pin3_state1',
            'pinevent_1420863326.123456_pin3_state0',
            'pinevent_1420863326.123456_pin2_state1',
            'xsfjef_fhejfec_dfhe',
            'pinevent_1420863326.456789_pin3_state2',
        ]

        ex = Exception('foo')

        def se_handle(fname, evt_datetime, pin, state):
            if fname == 'pinevent_1420863332.123456_pin2_state1':
                raise ex

        type(self.config).QUEUE_PATH = '/foo/bar'

        with patch('%s.logger' % pbm) as mock_logger:
            with patch('%s.os.listdir' % pbm) as mock_listdir:
                with patch('%s.handle_one_file' % pb) as mock_handle:
                    with patch('%s.os.unlink' % pbm) as mock_unlink:
                        mock_listdir.return_value = flist
                        mock_handle.side_effect = se_handle
                        self.cls.handle_files()
        assert mock_logger.mock_calls == [
            call.info("Found %d new events", 3),
            call.debug('File handled; removing: %s',
                       'pinevent_1420863326.123456_pin2_state1'),
            call.debug('File handled; removing: %s',
                       'pinevent_1420863326.123456_pin3_state0'),
            call.exception('Execption while handling event file %s',
                           'pinevent_1420863332.123456_pin2_state1'),
        ]
        assert mock_listdir.mock_calls == [call('/foo/bar')]
        assert mock_handle.mock_calls == [
            call('pinevent_1420863326.123456_pin2_state1',
                 datetime(2015, 1, 9, 23, 15, 26, 123456),
                 2, 1),
            call('pinevent_1420863326.123456_pin3_state0',
                 datetime(2015, 1, 9, 23, 15, 26, 123456),
                 3, 0),
            call('pinevent_1420863332.123456_pin2_state1',
                 datetime(2015, 1, 9, 23, 15, 32, 123456),
                 2, 1),
        ]
        assert mock_unlink.mock_calls == [
            call('/foo/bar/pinevent_1420863326.123456_pin2_state1'),
            call('/foo/bar/pinevent_1420863326.123456_pin3_state0')
        ]

    def test_handle_files_keyboard_interrupt(self):
        flist = [
            'pinevent_1420863332.123456_pin2_state1',
            'pinevent_1420863326.123456_pin3_state0',
        ]

        def se_handle(fname, evt_datetime, pin, state):
            if fname == 'pinevent_1420863332.123456_pin2_state1':
                raise KeyboardInterrupt

        type(self.config).QUEUE_PATH = '/foo/bar'

        with patch('%s.logger' % pbm) as mock_logger:
            with patch('%s.os.listdir' % pbm) as mock_listdir:
                with patch('%s.handle_one_file' % pb) as mock_handle:
                    with patch('%s.os.unlink' % pbm) as mock_unlink:
                        mock_listdir.return_value = flist
                        mock_handle.side_effect = se_handle
                        with pytest.raises(KeyboardInterrupt):
                            self.cls.handle_files()
        assert mock_logger.mock_calls == [
            call.info("Found %d new events", 2),
            call.debug('File handled; removing: %s',
                       'pinevent_1420863326.123456_pin3_state0'),
        ]
        assert mock_listdir.mock_calls == [call('/foo/bar')]
        assert mock_handle.mock_calls == [
            call('pinevent_1420863326.123456_pin3_state0',
                 datetime(2015, 1, 9, 23, 15, 26, 123456),
                 3, 0),
            call('pinevent_1420863332.123456_pin2_state1',
                 datetime(2015, 1, 9, 23, 15, 32, 123456),
                 2, 1),
        ]
        assert mock_unlink.mock_calls == [
            call('/foo/bar/pinevent_1420863326.123456_pin3_state0'),
        ]

    def test_handle_files_none(self):
        flist = [
            'foobar',
        ]
        type(self.config).QUEUE_PATH = '/foo/bar'

        with patch('%s.logger' % pbm) as mock_logger:
            with patch('%s.os.listdir' % pbm) as mock_listdir:
                with patch('%s.handle_one_file' % pb) as mock_handle:
                    with patch('%s.os.unlink' % pbm) as mock_unlink:
                        mock_listdir.return_value = flist
                        self.cls.handle_files()
        assert mock_logger.mock_calls == []
        assert mock_listdir.mock_calls == [call('/foo/bar')]
        assert mock_handle.mock_calls == []
        assert mock_unlink.mock_calls == []

    def test_handle_one_file(self):

        def se_exc(*argv):
            raise Exception()

        mock_cb1 = Mock()
        mock_cb2 = Mock()
        mock_cb2.side_effect = se_exc
        cbs = [mock_cb1, mock_cb2]

        pins = [
            {'name': 'pin0', 'states': ['pin0state0', 'pin0state1']},
            {'name': 'pin1', 'states': ['pin1state0', 'pin1state1']},
            {'name': 'pin2', 'states': ['pin2state0', 'pin2state1']},
            {'name': 'pin3', 'states': ['pin3state0', 'pin3state1']},
        ]

        type(self.config).CALLBACKS = cbs
        type(self.config).PINS = pins

        with patch('%s.logger' % pbm) as mock_logger:
            self.cls.handle_one_file(
                'myfname', datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0)
        assert mock_logger.mock_calls == [
            call.debug("Handling event: pin=%d state=%d dt=%s (%s)",
                       2, 0, datetime(2015, 2, 13, 1, 2, 3, 123456), 'myfname'),
            call.debug("Running callback: %s", mock_cb1),
            call.debug("Callback finished"),
            call.debug("Running callback: %s", mock_cb2),
            call.exception("Callback raised an exception."),
            call.debug("All callbacks finished.")
        ]
        assert mock_cb1.mock_calls == [
            call(datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0, 'pin2',
                 'pin2state0')
        ]
        assert mock_cb2.mock_calls == [
            call(datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0, 'pin2',
                 'pin2state0')
        ]

    def test_handle_one_file_keyboard_interrupt(self):

        def se_exc(*argv):
            raise KeyboardInterrupt()

        mock_cb1 = Mock()
        mock_cb2 = Mock()
        mock_cb2.side_effect = se_exc
        cbs = [mock_cb1, mock_cb2]

        pins = [
            {'name': 'pin0', 'states': ['pin0state0', 'pin0state1']},
            {'name': 'pin1', 'states': ['pin1state0', 'pin1state1']},
            {'name': 'pin2', 'states': ['pin2state0', 'pin2state1']},
            {'name': 'pin3', 'states': ['pin3state0', 'pin3state1']},
        ]

        type(self.config).CALLBACKS = cbs
        type(self.config).PINS = pins

        with patch('%s.logger' % pbm) as mock_logger:
            with pytest.raises(KeyboardInterrupt):
                self.cls.handle_one_file(
                    'myfname', datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0)
        assert mock_logger.mock_calls == [
            call.debug("Handling event: pin=%d state=%d dt=%s (%s)",
                       2, 0, datetime(2015, 2, 13, 1, 2, 3, 123456), 'myfname'),
            call.debug("Running callback: %s", mock_cb1),
            call.debug("Callback finished"),
            call.debug("Running callback: %s", mock_cb2),
        ]
        assert mock_cb1.mock_calls == [
            call(datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0, 'pin2',
                 'pin2state0')
        ]
        assert mock_cb2.mock_calls == [
            call(datetime(2015, 2, 13, 1, 2, 3, 123456), 2, 0, 'pin2',
                 'pin2state0')
        ]
