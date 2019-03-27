cone.ugm
========

Plugin for `cone.app <http://packages.python.org/cone.app>`_ providing user and
group management with LDAP as backend.

.. image:: http://bluedynamics.com/ugm.png


Features
--------

- Create, edit and delete users and groups
- Manage membership of users in groups
- Roles support
- Local Manager Support
- User and group form configuration
- POSIX support
- Samba support


Prerequirements
---------------

``lxml``, ``python-ldap`` and ``openldap`` get compiled, the required dev
headers must be installed on the system.

On debian based systems install:

.. code-block:: shell

    $ apt-get install libxml2-dev libxslt1-dev
    $ apt-get install libsasl2-dev libssl-dev libdb-dev

On ubuntu oneiric, you might need Berkeley v4.7 Database Libraries to make it
work:

.. code-block:: shell

    $ apt-get install libdb4.7-dev


Installation
------------

``cone.ugm`` contains a buildout configuration. Download and extract package
ZIP file, enter extraction location and run:

.. code-block:: shell

    cone.ugm$ python2.7 bootstrap.py
    cone.ugm$ ./bin/buildout

Start Test LDAP server with appropriate LDIF layer:

.. code-block:: shell

    cone.ugm$ ./bin/testldap start groupOfNames_10_10

Start the application:

.. code-block:: shell

    cone.ugm$ ./bin/paster serve ugm_groupOfNames_10_10.ini

and browse ``http://localhost:8081/``. Default ``admin`` user password is
``admin``.

The "roles" behavior in the principal form is only displayed if roles
configuration is sane. The LDIF imported for test layer does not provide the
roles container by default. Browse "Settings -> LDAP Roles" and perform
"create roles container" action if you want to enable roles in the demo.

**Note**: If ``python_ldap`` fails, don't use buildout offline mode!


Customization
=============

For customizing the plugin, make an integration package and include it in
buildout.


LDAP configuration
------------------

To define the LDAP configuration location add ``cone.ugm.ldap_config`` property
to application ini file, i.e.:

.. code-block:: ini

    cone.ugm.ldap_config = %(here)s/etc/ldap.xml


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


Default value callbacks
-----------------------

Depending on the LDAP object classes used for users and groups, more or less
attributes are required for the entries. Maybe not all of these attributes
should be visible to the user of ``cone.ugm``. Some might even require to be
computed. Therefore the plugin supports default value callbacks. These callbacks
get the principal node and id as attributes:

.. code-block:: python

    from cone.ugm import model

    def some_field_callback(node, id):
        return 'some computed value'

and are set to factory defaults for users and groups respectively:

.. code-block:: python

    model.factory_defaults.user['someField'] = some_field_callback

The factory defaults can also be static values:

.. code-block:: python

    model.factory_defaults.user['someField'] = '12345'


Form widgets
------------

The widgets used for attributes can also be customized. It expects a
``yafowil`` factory ``chain``, ``props`` and ``custom`` dicts which are passed
to ``yafowil`` factory. ``required`` flags field as required, and ``protected``
defines whether this field is not editable (like user id and group id):

.. code-block:: python

    from cone.ugm.browser import form_field_definitions

    user = form_field_definitions.user
    user['someField'] = dict()
    user['someField']['chain'] = 'field:label:error:text'
    user['someField']['props'] = dict()
    user['someField']['required'] = True
    user['someField']['protected'] = False


Samba support
-------------

Example configuration:

.. code-block:: python

    from cone.ugm import model
    from node.ext.ldap.ugm import posix
    from node.ext.ldap.ugm import shadow
    from node.ext.ldap.ugm import samba

    samba.SAMBA_LOCAL_SID = 'S-1-5-21-1234567890-1234567890-1234567890'
    samba.SAMBA_DEFAULT_DOMAIN = 'yourdomain'
    samba.SAMBA_PRIMARY_GROUP_SID = 'S-1-5-21-1234567890-1234567890-1234567890-123'

    user = model.factory_defaults.user
    user['gidNumber'] = posix.memberGid
    user['loginShell'] = posix.loginShell
    user['shadowFlag'] = shadow.shadowFlag
    user['shadowMin'] = shadow.shadowMin
    user['shadowMax'] = shadow.shadowMax
    user['shadowWarning'] = shadow.shadowWarning
    user['shadowInactive'] = shadow.shadowInactive
    user['shadowLastChange'] = shadow.shadowLastChange
    user['shadowExpire'] = shadow.shadowExpire
    user['sambaSID'] = samba.sambaUserSID
    user['sambaDomainName'] = samba.sambaDomainName
    user['sambaPrimaryGroupSID'] = samba.sambaPrimaryGroupSID
    user['sambaAcctFlags'] = samba.sambaAcctFlags
    user['sambaPwdLastSet'] = samba.sambaPwdLastSet

    group = model.factory_defaults.group
    model.factory_defaults.group['memberUid'] = posix.memberUid


Coverage Report
===============

::

    lines   cov%   module
       92    92%   cone.ugm.__init__
       43   100%   cone.ugm.browser.__init__
      278    68%   cone.ugm.browser.actions
       13   100%   cone.ugm.browser.authoring
       49    97%   cone.ugm.browser.autoincrement
       15   100%   cone.ugm.browser.columns
      135    71%   cone.ugm.browser.expires
      206    83%   cone.ugm.browser.group
       54    96%   cone.ugm.browser.groups
      241    94%   cone.ugm.browser.listing
       87    88%   cone.ugm.browser.portrait
       90    94%   cone.ugm.browser.principal
      100    96%   cone.ugm.browser.remote
       61    86%   cone.ugm.browser.roles
       15   100%   cone.ugm.browser.root
      387    42%   cone.ugm.browser.settings
      271    83%   cone.ugm.browser.user
       54    96%   cone.ugm.browser.users
        4   100%   cone.ugm.browser.utils
       13   100%   cone.ugm.layout
        9   100%   cone.ugm.model.__init__
       29   100%   cone.ugm.model.group
       75    90%   cone.ugm.model.groups
      166    91%   cone.ugm.model.localmanager
      215    83%   cone.ugm.model.settings
       29   100%   cone.ugm.model.user
       75    92%   cone.ugm.model.users
       22   100%   cone.ugm.model.utils
       58   100%   cone.ugm.testing.__init__
        1   100%   cone.ugm.tests.__init__
       44    97%   cone.ugm.tests.test_ugm


Contributors
============

- Robert Niederreiter (Author)
- Florian Friesdorf
- Jens Klein


Copyright
=========

Copyright (c) 2009-2019, BlueDynamics Alliance, Austria
All rights reserved.
