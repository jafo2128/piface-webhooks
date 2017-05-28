piface-webhooks
===============

.. image:: http://www.repostatus.org/badges/2.0.0/inactive.svg
   :alt: Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.
   :target: http://www.repostatus.org/#inactive

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
3. ``./support/puppetize.sh`` - this will use Puppet to install the system-wide dependencies and setup the project. If you don't want to use Puppet, the script and Puppet manifests are commented (to reproduce their actions manually, if you want). Note that I had some problems on my test system with ``virtualenv`` not installing. If you experience failures, ``apt-get install -y virtualenv`` and then run ``./puppetize.sh`` again.
4. Configure per the instructions below.
5. ``systemctl restart piface-listener; systemctl restart piface-worker`` to reload the new configuration.

If you want to pass options to the scripts, you can do so by editing ``/etc/default/piface-listener`` or ``/etc/default/piface-worker`` (respectively)
and placing in the content of the file, ``PIFACE_LISTENER_OPTS="<command line options here>"`` or ``PIFACE_WORKER_OPTS="<command line options here>"``.

Configuration
-------------

All components of piface-webhooks get their configuration from a Python module. For the simplest case (where you git cloned this repository),
copy ``piface_webhooks/settings.py.example`` to ``piface_webhooks/settings.py`` and edit the settings to your liking; descriptions of them
and what they do are in comments. If you wish to keep your settings outside of the git repository, you can use any importable Python module;
simply export the name of the module as the ``PIFACE_WEBHOOKS_SETTINGS_MODULE`` environment variable (inspired by `django settings <https://docs.djangoproject.com/en/1.9/topics/settings/>`_).

Simple Test/Foreground Operation
---------------------------------

1. In one shell/terminal, run ``piface-listener -vv`` (debug-level output).
2. In another, run ``piface-worker -vv`` (debug-level output).
3. Generate some input events, and watch it work.
