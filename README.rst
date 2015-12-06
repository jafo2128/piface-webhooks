piface-webhooks
===============

Python script/daemon to read RPi PiFace inputs and run a webhook when they change.

Installation
-------------

This assumes a Debian-based machine, like `Raspbian <>`_ or `OSMC <>`_. Run this as root; it will
install the project in ``/usr/local/piface-webhooks``.

1. ``apt-get update && apt-get install -y puppet git``
2. ``cd /usr/local && git clone https://github.com/jantman/piface-webhooks.git && cd piface-webhooks``
3. ``./puppetize.sh`` - this will use Puppet to install the system-wide dependencies and setup the project. If you don't want to use Puppet, the script and Puppet manifests are commented (to reproduce their actions manually, if you want). Note that I had some problems on my test system with ``virtualenv`` not installing. If you experience failures, ``apt-get install -y virtualenv`` and then run ``./puppetize.sh`` again.
4. Install your favorite text editor and edit ``piface-webhooks/settings.py``.
