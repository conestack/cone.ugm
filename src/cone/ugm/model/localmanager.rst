Local Manager
=============

Dummy environment.::

    >>> import os
    >>> import tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> conf_path = os.path.join(tempdir, 'localmanager.xml')

Local manager configuration object::
    
    >>> from cone.ugm.model.localmanager import LocalManagerConfig
    >>> config = LocalManagerConfig(conf_path)
    >>> config
    <cone.ugm.model.localmanager.LocalManagerConfig object at ...>

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
    ...     'default': 'bar',
    ... }
    
    >>> config['aaa'] = {
    ...     'target': ['bbb', 'ccc'],
    ...     'default': 'ccc',
    ... }

Iter::

    >>> list(config)
    ['foo', 'aaa']

Modify a rule::

    >>> rule = config['foo']['default'] = 'bar'

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
    '    <default>bar</default>', 
    '  </foo>', 
    '  <aaa>', 
    '    <target>', 
    '      <item>bbb</item>', 
    '      <item>ccc</item>', 
    '    </target>', 
    '    <default>ccc</default>', 
    '  </aaa>', 
    '</localmanager>', 
    '']

Recreate on existing conf::

    >>> config = LocalManagerConfig(conf_path)
    >>> config.items()
    [('foo', {'default': 'bar', 'target': ['bar', 'baz']}), 
    ('aaa', {'default': 'ccc', 'target': ['bbb', 'ccc']})]
