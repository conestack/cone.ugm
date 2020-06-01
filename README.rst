cone.ugm
========

Plugin for `cone.app <http://packages.python.org/cone.app>`_ providing a
user and group management UI.

.. image:: http://bluedynamics.com/ugm.png


Features
--------

- Create, edit and delete users and groups
- Manage membership of users in groups
- Roles support
- Local Manager Support
- User and group form configuration


Development Setup
=================

Prerequirements
---------------

``lxml`` gets compiled, the required dev headers must be installed on the system.

On debian based systems install:

.. code-block:: shell

    $ apt-get install -y libxml2-dev libxslt1-dev


Installation
------------

``cone.ugm`` contains a buildout configuration. Download or checkout package
and run:

.. code-block:: shell

    cone.ugm$ ./bootstrap.sh python3

Start the application:

.. code-block:: shell

    cone.ugm$ ./bin/pserver ugm.ini

and browse ``http://localhost:8081/``. Default ``admin`` user password is
``admin``.


Configuration and Customization
===============================

General
-------

For customizing the plugin, make an integration package and include it in
your setup.


Roles
-----

``cone.ugm`` internally uses 3 roles in order to permit user actions.

``editor`` is permitted to manage membership, ``admin`` additionally is
permitted to add, edit and delete users and groups, and ``manager`` is a
superuser. If UGM is the only plugin used, you can reduce the available roles
to this three:

.. code-block:: python

    cone.app.security.DEFAULT_ROLES = [
        ('editor', 'Editor'),
        ('admin', 'Admin'),
        ('manager', 'Manager')
    ]


Principal Forms
---------------

XXX


Contributors
============

- Robert Niederreiter (Author)
- Florian Friesdorf
- Jens Klein


Copyright
=========

Copyright (c) 2009-2019, BlueDynamics Alliance, Austria
All rights reserved.
