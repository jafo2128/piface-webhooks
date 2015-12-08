#!/bin/bash -ex
#
# Wrapper to install piface-webhooks with puppet.
#
# The latest version of this package is available at:
# <https://github.com/jantman/piface_webhooks>
#
################################################################################
# Copyright 2015 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
#
#    This file is part of piface_webhooks.
#
#    piface_webhooks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    piface_webhooks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with piface_webhooks.  If not, see <http://www.gnu.org/licenses/>.
#
# The Copyright and Authors attributions contained herein may not be removed or
# otherwise altered, except to add the Author attribution of a contributor to
# this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
# While not legally required, I sincerely request that anyone who finds
# bugs please submit them at <https://github.com/jantman/piface_webhooks> or
# to me via email, and that you send any contributions or improvements
# either as a pull request on GitHub, or to me via email.
################################################################################
#
# AUTHORS:
# Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################

INSTALL_PATH=/usr/local/piface-webhooks
mypath=$(realpath $0)

if [[ "$mypath" != "${INSTALL_PATH}/support/puppetize.sh" ]]; then
    >&2 echo "ERROR: this script and the related puppet module expect the git repository to be cloned under ${INSTALL_PATH}"
    >&2 echo "You seem to be running from an alternate path (this file: ${mypath})"
    >&2 echo "Please either clone/move to the right location, or edit INSTALL_PATH in puppetize.sh and"
    >&2 echo "\$install_path in piface_webhooks_dependencies.pp"
    exit 1
fi

# setup kernel module - see http://pifacecommon.readthedocs.org/en/latest/installation.html#enable-the-spi-module
if [[ -e /etc/modprobe.d/raspi-blacklist.conf ]]; then
    # kernel < 3.18
    sed -i 's/^blacklist spi-bcm2708/# blacklist spi-bcm2708/' /etc/modprobe.d/raspi-blacklist.conf
    echo "Added SPI (GPIO) module to /boot/config.txt; you must now reboot and then re-run this script."
    exit 1
else
    # kernel >= 3.18
    if ! grep 'dtparam=spi=on' /boot/config.txt; then
        echo "dtparam=spi=on" >> /boot/config.txt
        echo "Added SPI (GPIO) module to /boot/config.txt; you must now reboot and then re-run this script."
        exit 1
    fi
fi

if ! lsmod | grep spi_bcm2708; then
    echo "ERROR: spi-bcm2708 module not seen in 'lsmod' output; something is wrong!"
    exit 1
fi

puppet apply -t piface_webhooks_dependencies.pp
