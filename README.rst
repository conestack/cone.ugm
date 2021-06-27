.. image:: https://img.shields.io/pypi/v/cone.ugm.svg
    :target: https://pypi.python.org/pypi/cone.ugm
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/cone.ugm.svg
    :target: https://pypi.python.org/pypi/cone.ugm
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/bluedynamics/cone.ugm.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/cone.ugm

.. image:: https://coveralls.io/repos/github/bluedynamics/cone.ugm/badge.svg?branch=master
    :target: https://coveralls.io/github/bluedynamics/cone.ugm?branch=master

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

The basic principal form customization happens in the ugm XML configuration
file. Each field to render must have an entry in ``users_form_attrmap``
respective ``groups_form_attrmap``:

.. code-block:: xml

  <users_form_attrmap>
    <elem>
      <key>my_field</key>
      <value>My Field</value>
    </elem>
  </users_form_attrmap>

By default, a non required text field gets rendered for each custom entry in
the XML configuration.

To make a custom field required, the easiest way is to use
``default_form_field_factory`` and register it with ``user_field``
respective ``group_field``:

.. code-block:: python

    from cone.ugm.browser.principal import default_form_field_factory
    from cone.ugm.browser.principal import user_field
    from functools import partial

    my_field_factory = user_field('my_field')(
        partial(default_form_field_factory, required=True)
    )

It's possible to register custom principal field factories for dedicated
UGM backends. This example is taken from ``cone.ldap`` and registers a
user field factory for ``cn`` attribute in ``ldap`` backend:

.. code-block:: python

    ldap_cn_field_factory = user_field('cn', backend='ldap')(
        partial(default_form_field_factory, required=True)
    )

The most flexible way for principal form field customization is to provide
a callback function and call the yafowil factory directly:

.. code-block:: python

    from yafowil.base import factory

    @user_field('age')
    def age_field_factory(form, label, value):
        return factory(
            'field:label:error:number',
            value=value,
            props={
                'label': label,
                'datatype': int
            })

Note. The value of the custom field gets written to principal attributes as
extracted from the widget. Make sure to define the expected datatype in the
widget properties or define a suitable custom extractor.


Principal Listings
------------------

XXX


Object Events
=============

You can react to creation, modification and deletion of users and groups by
binding to the given event classes.

These events are fired when the user manipulations are done in the UGM 
management forms.

necessary imports:

.. code-block:: python

    from zope.event import classhandler
    from cone.ugm import events


Defining the event handlers
---------------------------

for users:

.. code-block:: python

    @classhandler.handler(events.UserCreatedEvent)
    def on_user_created(event):
        print(f"user {event.principal} with id {event.principal.name} created")

    @classhandler.handler(events.UserModifiedEvent)
    def on_user_modified(event):
        print(f"user {event.principal} with id {event.principal.name} modified")

    @classhandler.handler(events.UserDeletedEvent)
    def on_user_deleted(event):
        print(f"user {event.principal} with id {event.principal.name} deleted")

and for groups:

.. code-block:: python

    @classhandler.handler(events.GroupCreatedEvent)
    def on_group_created(event):
        print(f"group {event.principal} with id {event.principal.name} created")

    @classhandler.handler(events.GroupModifiedEvent)
    def on_group_modified(event):
        print(f"group {event.principal} with id {event.principal.name} modified")

    @classhandler.handler(events.GroupDeletedEvent)
    def on_group_deleted(event):
        print(f"group {event.principal} with id {event.principal.name} deleted")


Contributors
============

- Robert Niederreiter (Author)
- Florian Friesdorf
- Jens Klein
