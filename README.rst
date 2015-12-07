piface-webhooks
===============

Python script/daemon to read RPi PiFace inputs and run a webhook (or other callback) when they change.

Overview
--------

This package is made up of two components; the listner and the worker. Each one has a separate console
entry point, and is intended to be run as a separate process/daemon. The listener (``piface-listener``)
listens to input pin change events from the PiFace, and creates files on disk (a simple disk-based queue)
for every event. The worker (``piface-worker``) finds these new files, and executes the configured tasks
for each event, in order.

Installation
-------------

This assumes a Debian-based machine, like `Raspbian <>`_ or `OSMC <>`_. Run this as root; it will
install the project in ``/usr/local/piface-webhooks``.

1. ``apt-get update && apt-get install -y puppet git``
2. ``cd /usr/local && git clone https://github.com/jantman/piface-webhooks.git && cd piface-webhooks``
3. ``./puppetize.sh`` - this will use Puppet to install the system-wide dependencies and setup the project. If you don't want to use Puppet, the script and Puppet manifests are commented (to reproduce their actions manually, if you want). Note that I had some problems on my test system with ``virtualenv`` not installing. If you experience failures, ``apt-get install -y virtualenv`` and then run ``./puppetize.sh`` again.
4. Install your favorite text editor and edit ``piface-webhooks/settings.py``.

Configuration
-------------

Edit ``setup.py``.

Simple Test/Foreground Operation
---------------------------------

1. In one shell/terminal, run ``piface-listener -vv`` (debug-level output).
2. In another, run ``piface-worker -vv`` (debug-level output).
3. Generate some input events, and watch it work.
