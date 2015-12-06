piface-webhooks
===============

Python script/daemon to read RPi PiFace inputs and run a webhook when they change.

Installation
-------------

This assumes a Debian-based machine, like `Raspbian <>`_ or `OSMC <>`_. Run this as root:

1. ``apt-get update && apt-get install -y puppet git``
2. ``cd /usr/local && git clone https://github.com/jantman/piface-webhooks.git && cd piface-webhooks``
3. ``puppet apply piface_webhooks_dependencies.pp`` - this will install all system-level dependencies (python3, virtualenv, pip)
4. ``puppet apply piface_webhooks_setup.pp`` - this will create the virtualenv, install the package and set it up to run as a service
5. 
