"""
config.py

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
import importlib
import logging

logger = logging.getLogger()

#: Name of module to load custom settings from
ENV_VAR_NAME = 'PIFACE_WEBHOOKS_SETTINGS_MODULE'
DEFAULT_MODULE = 'piface_webhooks.settings'


class Config(object):

    def __init__(self):
        """initialize the config with defaults and then load settings"""
        self._set_defaults()
        self._load_settings()

    def _load_settings(self):
        modname = os.environ.get(ENV_VAR_NAME, DEFAULT_MODULE)
        logger.debug("Loading settings from %s", modname)
        mod = self._load_module(modname)
        if mod is None:
            logger.error("Settings module %s could not be loaded; using "
                         "default settings!", modname)
            return
        for setting in dir(mod):
            if not setting.isupper():
                continue
            val = getattr(mod, setting)
            setattr(self, setting, val)

    def _load_module(self, modname):
        """
        Load a module specified by modname and return it, or None if it fails.
        """
        try:
            mod = importlib.import_module(modname)
        except:
            logger.exception("Exception while importing settings module %s",
                             modname)
            return None
        return mod

    def _set_defaults(self):
        self.QUEUE_PATH = '/var/spool/piface-webhooks'
        self.NO_LEDS = False
        self.INVERT_LED = False
        self.PINS = [
            {'name': 'Pin 0', 'states': ['off', 'on']},
            {'name': 'Pin 1', 'states': ['off', 'on']},
            {'name': 'Pin 2', 'states': ['off', 'on']},
            {'name': 'Pin 3', 'states': ['off', 'on']},
        ]
        self.CALLBACKS = []
