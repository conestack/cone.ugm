cone.ugm.model.utils
====================

::

    >>> from cone.app import root
    >>> from cone.ugm.model.utils import (
    ...     ugm_server,
    ...     ugm_users,
    ...     ugm_groups,
    ...     ugm_backend,
    ... )

    >>> ugm_server(root)
    <ServerSettings object 'ugm_server' at ...>
    
    >>> ugm_users(root)
    <UsersSettings object 'ugm_users' at ...>
    
    >>> ugm_groups(root)
    <GroupsSettings object 'ugm_groups' at ...>
    
    >>> import cone.app
    >>> cone.app.backend = None
    
    >>> backend = ugm_backend(root)
    >>> backend
    <Ugm object 'ugm' at ...>
    
    >>> backend is ugm_backend(root)
    True
    
    >>> import cone.ugm
    >>> cone.ugm.backend = None
    >>> backend is ugm_backend(root)
    False
