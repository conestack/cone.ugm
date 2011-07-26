import cone.app
from cone.app.model import Properties
from cone.ugm.model.settings import (
    ServerSettings,
    UsersSettings,
    GroupsSettings,
)
from cone.ugm.model.users import Users
from cone.ugm.model.groups import Groups


# custom UGM styles
cone.app.cfg.css.protected.append('cone.ugm.static/styles.css')


# custom UGM javascript
cone.app.cfg.js.protected.append('cone.ugm.static/ugm.js')


# layout configuration
cone.app.cfg.layout.livesearch = False
cone.app.cfg.layout.pathbar = False
cone.app.cfg.layout.sidebar_left = []


# UGM settings
cone.app.register_plugin_config('ugm_server', ServerSettings)
cone.app.register_plugin_config('ugm_users', UsersSettings)
cone.app.register_plugin_config('ugm_groups', GroupsSettings)


# Users container
cone.app.register_plugin('users', Users)


# Groups container
cone.app.register_plugin('groups', Groups)


# The node.ext.ugm implementation to use for user and group management
# currently only LDAP
backend = None