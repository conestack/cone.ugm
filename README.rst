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
- User and group form configuration
- POSIX support
- Samba support


Prerequirements
---------------

``lxml``, ``python-ldap`` and ``openldap`` get compiled, the required dev
headers must be installed on the system.

On debian based systems install::

    $ apt-get install libxml2-dev libxslt1-dev
    $ apt-get install libsasl2-dev libssl-dev libdb-dev

On ubuntu oneiric, you might need Berkeley v4.7 Database Libraries to make it
work::

    $  apt-get install libdb4.7-dev

Installation
------------

``cone.ugm`` contains a buildout configuration. Download and extract package
ZIP file, enter extraction location and run::

    cone.ugm$ python2.6 bootstrap.py -c dev.cfg
    cone.ugm$ ./bin/buildout -c dev.cfg

Start Test LDAP server with appropriate LDIF layer::

    cone.ugm$ ./bin/testldap start groupOfNames_10_10

Start the application::

    cone.ugm$ ./bin/paster serve ugm.ini

and browse ``http://localhost:8081/``. Default ``admin`` user password is
``admin``.

The "roles" part in the principal form is only displayed if roles configuration
is sane. The LDIF imported for test layer does not provide the roles container
by default. Browse "Settings -> LDAP Roles" and perform "create roles container"
action if you want to enable roles in the demo.


Customization
=============

For customizing the plugin, make an integration package and include it in
buildout.


Roles
-----

``cone.ugm`` internally uses 3 roles in order to permit user actions.

``editor`` is permitted to manage membership, ``admin`` additionally is
permitted to add, edit and delete users and groups, and ``manager`` is a
superuser. If UGM is the only plugin used, you can reduce the available roles
to this three::

    >>> cone.app.security.DEFAULT_ROLES = [
    ...     ('editor', 'Editor'),
    ...     ('admin', 'Admin'),
    ...     ('manager', 'Manager'),
    ... ]


Default value callbacks
-----------------------

Depending on the LDAP object classes used for users and groups, more or less
attributes are required for the entries. Maybe not all of these attributes
should be visible to the user of ``cone.ugm``. Some might even require to be
computed. Therefore the plugin supports default value callbacks. These callbacks
get the principal node and id as attributes::

    >>> from cone.ugm import model

    >>> def some_field_callback(node, id):
    ...     return 'some computed value'

and are set to factory defaults for users and groups respectively::

    >>> model.factory_defaults.user['someField'] = some_field_callback

The factory defaults can also be static values::

    >>> model.factory_defaults.user['someField'] = '12345'


Form widgets
------------

The widgets used for attributes can also be customized. It expects a
``yafowil`` factory ``chain``, ``props`` and ``custom`` dicts which are passed
to ``yafowil`` factory. ``required`` flags field as required, and ``protected``
defines whether this field is not editable (like user id and group id)::

    >>> from cone.ugm.browser import form_field_definitions
    >>> user = form_field_definitions.user
    >>> user['someField'] = dict()
    >>> user['someField']['chain'] = 'field:label:error:text'
    >>> user['someField']['props'] = dict()
    >>> user['someField']['required'] = True
    >>> user['someField']['protected'] = False


Samba support
-------------

Example configuration::

    >>> from node.ext.ldap.ugm import (
    ...     posix,
    ...     shadow,
    ...     samba,
    ... )

    >>> samba.SAMBA_LOCAL_SID = 'S-1-5-21-1234567890-1234567890-1234567890'
    >>> samba.SAMBA_DEFAULT_DOMAIN = 'yourdomain'
    >>> samba.SAMBA_PRIMARY_GROUP_SID = 'S-1-5-21-1234567890-1234567890-1234567890-123'

    >>> from cone.ugm import model

    >>> user = model.factory_defaults.user
    >>> user['gidNumber'] = posix.memberGid
    >>> user['loginShell'] = posix.loginShell
    >>> user['shadowFlag'] = shadow.shadowFlag
    >>> user['shadowMin'] = shadow.shadowMin
    >>> user['shadowMax'] = shadow.shadowMax
    >>> user['shadowWarning'] = shadow.shadowWarning
    >>> user['shadowInactive'] = shadow.shadowInactive
    >>> user['shadowLastChange'] = shadow.shadowLastChange
    >>> user['shadowExpire'] = shadow.shadowExpire
    >>> user['sambaSID'] = samba.sambaUserSID
    >>> user['sambaDomainName'] = samba.sambaDomainName
    >>> user['sambaPrimaryGroupSID'] = samba.sambaPrimaryGroupSID
    >>> user['sambaAcctFlags'] = samba.sambaAcctFlags
    >>> user['sambaPwdLastSet'] = samba.sambaPwdLastSet

    >>> group = model.factory_defaults.group
    >>> model.factory_defaults.group['memberUid'] = posix.memberUid


TODO
====

- move LDAP related code to ``cone.ldap``
- make UI work with any kind of ``node.ext.ugm`` based implementations.
- provide application model for ``node.ext.ugm.file`` implementation as default.
- Listing batches.
- DnD membership assignment


Contributors
============

- Robert Niederreiter <rnix [at] squarewave [dot] at>

- Florian Friesdorf <flo [at] chaoflow [dot] net>

- Jens Klein <jens [at] bluedynamics [dot] com>


History
=======

0.9.1dev
--------

- Get rid of global ``cone.ugm.backend``. ``cone.app.cfg.auth`` is returend
  by ``cone.ugm.model.utils.ugm_backend``.
  [rnix, 2011-11-22]

- Explicit names for settings forms.
  [rnix, 2011-11-18]

- Add node properties for users and groups to get displayed in navtree if
  displayed.
  [rnix, 2011-11-16]


0.9
---

- Initial release.
