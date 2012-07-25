Local Manager
=============

Dummy environment.::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> conf_path = os.path.join(tempdir, 'localmanager.xml')

Local manager configuration attributes::
    
    >>> from cone.ugm.model.localmanager import LocalManagerConfigAttributes
    >>> config = LocalManagerConfigAttributes(conf_path)
    >>> config
    <LocalManagerConfigAttributes object 'None' at ...>

Not exists yet::

    >>> os.path.exists(conf_path)
    False

After calling it does::

    >>> config()
    >>> os.path.exists(conf_path)
    True
    
    >>> with open(conf_path) as handle:
    ...     handle.read().split('\n')
    ['<localmanager/>', '']

Add rules::

    >>> config['foo'] = {
    ...     'target': ['bar', 'baz'],
    ...     'default': ['bar'],
    ... }
    
    >>> config['aaa'] = {
    ...     'target': ['bbb', 'ccc'],
    ...     'default': ['ccc'],
    ... }

Iter::

    >>> list(config)
    ['foo', 'aaa']

Modify a rule::

    >>> rule = config['foo']['default'] = ['bar']

Write config to file::

    >>> config()
    >>> with open(conf_path) as handle:
    ...     handle.read().split('\n')
    ['<localmanager>', 
    '  <foo>', 
    '    <target>', 
    '      <item>bar</item>', 
    '      <item>baz</item>', 
    '    </target>', 
    '    <default>', 
    '      <item>bar</item>', 
    '    </default>', 
    '  </foo>', 
    '  <aaa>', 
    '    <target>', 
    '      <item>bbb</item>', 
    '      <item>ccc</item>', 
    '    </target>', 
    '    <default>', 
    '      <item>ccc</item>', 
    '    </default>', 
    '  </aaa>', 
    '</localmanager>', 
    '']

Recreate on existing conf::

    >>> config = LocalManagerConfigAttributes(conf_path)
    >>> config.items()
    [('foo', {'default': ['bar'], 'target': ['bar', 'baz']}), 
    ('aaa', {'default': ['ccc'], 'target': ['bbb', 'ccc']})]

Local manager ACL::

    >>> from cone.app import get_root
    >>> root = get_root()
    
    >>> localmanager_settings = root['settings']['ugm_localmanager']
    >>> localmanager_settings
    <LocalManagerSettings object 'ugm_localmanager' at ...>
    
    >>> users = root['users']
    >>> users
    <Users object 'users' at ...>
    
    >>> groups = root['groups']
    >>> groups
    <Groups object 'groups' at ...>

Cleanup::

    >>> import shutil
    >>> shutil.rmtree(tempdir)
