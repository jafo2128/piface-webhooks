"""
worker.py

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

import os
import sys
import argparse
import logging
import re
from datetime import datetime

from piface_webhooks.version import VERSION
from piface_webhooks.config import Config

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


class Worker(object):

    fname_re = re.compile(r'^pinevent_([0-9]+\.[0-9]+)_pin([0-9]+)_state(0|1)$')

    def __init__(self):
        self.config = Config()
        logger.info("Initializing worker")
        self.process_events = True

    def run(self):
        """loop waiting for files, handle them when present"""
        # this function is a hack for unit testing
        logger.info("Beginning file handling loop")
        while self._alwaystrue():
            self.handle_files()

    def handle_files(self):
        """Check for new files, and handle them in order if present"""
        handle = {}
        for fname in os.listdir(self.config.QUEUE_PATH):
            m = self.fname_re.match(fname)
            if not m:
                continue
            ts = float(m.group(1))
            dt = datetime.fromtimestamp(ts)
            handle[fname] = (dt, int(m.group(2)), int(m.group(3)))
        if len(handle) < 1:
            return
        logger.info("Found %d new events", len(handle))
        for fname, event in sorted(handle.items()):
            try:
                self.handle_one_file(fname, event[0], event[1], event[2])
                logger.debug("File handled; removing: %s", fname)
                os.unlink(os.path.join(self.config.QUEUE_PATH, fname))
            except:
                logger.exception("Execption while handling event file %s",
                                 fname)

    def handle_one_file(self, fname, evt_datetime, pin, state):
        logger.debug("Handling event: pin=%d state=%d dt=%s (%s)",
                     pin, state, evt_datetime, fname)
        for cb in self.config.CALLBACKS:
            logger.debug("Running callback: %s", cb)
            try:
                cb(evt_datetime, pin, state, self.config.PINS[pin]['name'],
                   self.config.PINS[pin]['states'][state])
                logger.debug("Callback finished")
            except:
                logger.exception("Callback raised an exception.")
        logger.debug("All callbacks finished.")

    def _alwaystrue(self):
        """hack for unit testing sanely"""
        return True

    def console_entry_point(self):
        """entry point to handle args and call run function"""
        args = self.parse_args(sys.argv[1:])
        if args.version:
            print("pyface-webhooks %s "
                  "<https://github.com/jantman/piface_webhooks>" % VERSION)
            raise SystemExit(0)
        if args.verbose == 1:
            logger.warning("Setting log level to INFO")
            logger.setLevel(logging.INFO)
        elif args.verbose > 1:
            logger.warning("Setting log level to DEBUG")
            # debug-level logging hacks
            FORMAT = "[%(asctime)s][%(levelname)s %(filename)s:%(lineno)s - " \
                     "%(name)s.%(funcName)s() ] %(message)s"
            debug_formatter = logging.Formatter(fmt=FORMAT)
            logger.handlers[0].setFormatter(debug_formatter)
            logger.setLevel(logging.DEBUG)
        self.process_events = args.process_events
        self.run()

    def parse_args(self, argv):
        """
        parse arguments/options

        :param argv: argument list to parse, usually ``sys.argv[1:]``
        :type argv: list
        :returns: parsed arguments
        :rtype: :py:class:`argparse.Namespace`
        """
        desc = 'PiFace input change event queue processor/worker'
        p = argparse.ArgumentParser(description=desc)
        p.add_argument('-w', '--no-process', dest='process_events',
                       action='store_false', default=True,
                       help='do not process events, just log what would be '
                       'done (note this will cause events to pile up on disk)')
        p.add_argument('-v', '--verbose', dest='verbose', action='count',
                       default=0,
                       help='verbose output. specify twice for debug-level '
                       'output.')
        p.add_argument('-V', '--version', dest='version', action='store_true',
                       default=False,
                       help='print version number and exit.')
        args = p.parse_args(argv)
        return args


def console_entry_point():
    r = Worker()
    r.console_entry_point()


if __name__ == "__main__":
    console_entry_point()
