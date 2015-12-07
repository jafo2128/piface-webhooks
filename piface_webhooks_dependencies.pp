# piface_webhooks_dependencies.pp
#
# Puppet manifest to install system-level dependencies for piface-webhooks
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

if $::osfamily != 'Debian' {
  fail("piface-webhooks Puppet is only compatible with Debian.")
}

$install_path = '/usr/local/piface-webhooks'

$packages = ['python3', 'python3-pip', 'python3-virtualenv', 'python3-dev']

package {$packages:
  ensure => present,
} ->

# create the virtualenv
exec {'make-virtualenv':
  command => "/usr/bin/virtualenv -p /usr/bin/python3 ${install_path}",
  creates => "${install_path}/bin/pip",
  user    => 'root',
} ->

# install the git clone in the virtualenv
# this always runs, so that it updates any entry points
exec {'install-package':
  command => "${install_path}/bin/python setup.py develop",
  cwd     => $install_path,
  user    => 'root',
}
