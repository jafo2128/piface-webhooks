"""
listener.py

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

from pifacedigitalio import (PiFaceDigital, InputEventListener, IODIR_ON,
                             IODIR_OFF)

import piface_webhooks.settings as settings
from piface_webhooks.version import VERSION

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()


class Listener(object):

    def __init__(self):
        logger.info("Initializing listener")
        self.write_files = True

    def run(self):
        """initialize and run the PiFaceWebhookApp"""
        logger.debug("initializing chip")
        self.chip = PiFaceDigital()
        logger.debug("chip initialized")
        logger.debug("creating InputEventListener")
        self.listener = InputEventListener(chip=self.chip)
        for i in range(4):
            logger.debug("registering callback for %s ON", i)
            self.listener.register(i, IODIR_ON, self.handle_input_on)
            logger.debug("registering callback for %s OFF", i)
            self.listener.register(i, IODIR_OFF, self.handle_input_off)
        logger.debug("activating listener")
        self.listener.activate()
        logger.warning("Listener exited")

    def handle_input_on(self, event):
        """
        InputEventListener callback function for IODIR_ON (pin on)

        :param event: the event that was detected
        :type event: pifacecommon.interrupts.InterruptEvent
        """
        logger.info("Received ON event for pin %s", event.pin_num)
        self.handle_change(event.pin_num, True, event.timestamp)
        # now set the LED
        logger.debug("Setting output %s on", event.pin_num)
        self.chip.output_pins[event.pin_num].turn_on()
        logger.debug("Set output %s on", event.pin_num)

    def handle_input_off(self, event):
        """
        InputEventListener callback function for IODIR_OFF (pin off)

        :param event: the event that was detected
        :type event: pifacecommon.interrupts.InterruptEvent
        """
        logger.info("Received OFF event for pin %s", event.pin_num)
        self.handle_change(event.pin_num, False, event.timestamp)
        # now set the LED
        logger.debug("Setting output %s off", event.pin_num)
        self.chip.output_pins[event.pin_num].turn_off()
        logger.debug("Set output %s off", event.pin_num)

    def handle_change(self, pin_num, state, timestamp):
        """
        Handler for pin state change.

        :param pin_num: the pin number that changed
        :type pin_num: int
        :param state: the new state of the pin (True for on, False for off)
        :type state: bool
        :param timestamp: timestamp when the event happened (Float unix TS)
        :type timestamp: float
        """
        state_name = 'off'
        if state:
            state_name = 'on'
        fname = 'pinevent_%s_%s_%s' % (timestamp, pin_num, state_name)
        fpath = os.path.join(settings.QUEUE_PATH, fname)
        if not self.write_files:
            logger.warning('Would create event file: %s', fpath)
            return
        # touch the file
        with open(fpath, 'a'):
            os.utime(fpath, None)
        logger.debug('Created event file: %s', fpath)

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
        self.write_files = args.write_files
        self.run()

    def parse_args(self, argv):
        """
        parse arguments/options

        :param argv: argument list to parse, usually ``sys.argv[1:]``
        :type argv: list
        :returns: parsed arguments
        :rtype: :py:class:`argparse.Namespace`
        """
        desc = 'Listen for PiFace input changes and queue them to disk'
        p = argparse.ArgumentParser(description=desc)
        p.add_argument('-w', '--no-write', dest='write_files',
                       action='store_false', default=True,
                       help='do not write queue files; just log changes')
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
    r = Listener()
    r.console_entry_point()


if __name__ == "__main__":
    console_entry_point()
