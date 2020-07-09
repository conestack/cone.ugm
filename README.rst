Plugin for `cone.app <http://packages.python.org/cone.app>`_ providing a
user and group management UI.


Features
--------

- Users and Groups CRUD
- Principal membership of users and groups
- Roles support
- Local Manager Support
- User and group form configuration


Setup
=====

Prerequirements
---------------

While installation ``lxml`` gets compiled, the required dev headers must be
installed on the system.

On debian based systems install:

.. code-block:: shell

    $ apt-get install -y libxml2-dev libxslt1-dev


Development and Testing
-----------------------

For testing and development, ``cone.ugm`` contains a buildout configuration.
Download or checkout package and run:

.. code-block:: shell

    cone.ugm$ ./bootstrap.sh python3


Example Configuration
---------------------

For testing and demo purposes, an example UGM configuration is contained in the
``cfg`` folder of the source package.

It contains the configuration file ``ugm.xml``, containing the general UGM
configuration and ``localmanager.xml``, containing the configuration about
local users and groups management. These two files can be edited TTW via the
settings UI.

The ``ugm.ini`` file contains the application configuration:

.. code-block:: ini

    [app:ugm]
    ...

    cone.plugins =
        cone.ugm

    ugm.backend = file
    ugm.config = %(here)s/ugm.xml
    ugm.localmanager_config = %(here)s/localmanager.xml

    ugm.users_file = %(here)s/../parts/ugm/users
    ugm.groups_file = %(here)s/../parts/ugm/groups
    ugm.roles_file = %(here)s/../parts/ugm/roles
    ugm.datadir = %(here)s/../parts/ugm/data

    ...

In this example the ``file`` backend is configured as UGM backend. For
configuring SQL or LDAP based backends, see documentation at ``cone.sql``
respective ``cone.ldap``.

Start the application:

.. code-block:: shell

    cone.ugm$ ./bin/pserver cfg/ugm.ini

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

Copyright (c) 2009-2020, BlueDynamics Alliance, Austria
All rights reserved.
