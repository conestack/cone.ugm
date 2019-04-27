cone.ugm.model.utils
====================

::

    >>> from cone.app import root
    >>> from cone.app.ugm import ugm_backend
    >>> from cone.ugm.model.utils import ugm_groups
    >>> from cone.ugm.model.utils import ugm_server
    >>> from cone.ugm.model.utils import ugm_users

    >>> ugm_server(root)
    <ServerSettings object 'ugm_server' at ...>

    >>> ugm_users(root)
    <UsersSettings object 'ugm_users' at ...>

    >>> ugm_groups(root)
    <GroupsSettings object 'ugm_groups' at ...>

    >>> ugm_backend.name
    'ldap'

    >>> backend = ugm_backend.ugm
    >>> backend
    <Ugm object 'ldap_ugm' at ...>

    >>> backend is ugm_backend.ugm
    True

    >>> ugm_backend.initialize()
    >>> backend is ugm_backend.ugm
    False
