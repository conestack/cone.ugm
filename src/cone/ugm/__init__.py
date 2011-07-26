import cone.app
from cone.app.model import Properties
from cone.ugm.model.settings import (
    ServerSettings,
    UsersSettings,
    GroupsSettings,
)
from cone.ugm.model.users import Users
from cone.ugm.model.groups import Groups
from yafowil.common import ascii_extractor

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

# user and group factory defaults
factory_defaults = Properties()
factory_defaults.user = dict()
factory_defaults.group = dict()

# user and group form field definitions for yafowil
# overwrite or extend in integration __init__
# XXX: future -> yafowil form field properties editor
# XXX: far future -> yafowil JS form editor
# XXX: user and group form schema definitions should then be resolved in order
#      yafowil browser based cfg -> default cfg -> general default
form_field_definitions = Properties()
form_field_definitions.user = dict()
form_field_definitions.group = dict()

# user default
form_field_definitions.user['default'] = dict()
form_field_definitions.user['default']['chain'] = 'field:label:error:text'
form_field_definitions.user['default']['required'] = False
form_field_definitions.user['default']['protected'] = False

# user id
form_field_definitions.user['id'] = dict()
form_field_definitions.user['id']['chain'] = \
    'field:*ascii:*exists:label:error:text'
form_field_definitions.user['id']['props'] = dict()
form_field_definitions.user['id']['props']['ascii'] = True
form_field_definitions.user['id']['custom'] = dict()
form_field_definitions.user['id']['custom']['ascii'] = \
    ([ascii_extractor], [], [], [], [])
form_field_definitions.user['id']['custom']['exists'] = \
    (['context.exists'], [], [], [], [])
form_field_definitions.user['id']['required'] = True
form_field_definitions.user['id']['protected'] = True

# user login
form_field_definitions.user['login'] = dict()
form_field_definitions.user['login']['chain'] = 'field:*ascii:label:error:text'
form_field_definitions.user['login']['props'] = dict()
form_field_definitions.user['login']['props']['ascii'] = True
form_field_definitions.user['login']['custom'] = dict()
form_field_definitions.user['login']['custom']['ascii'] = \
    ([ascii_extractor], [], [], [], [])
form_field_definitions.user['login']['required'] = True
form_field_definitions.user['login']['protected'] = True

# user mail
form_field_definitions.user['mail'] = dict()
form_field_definitions.user['mail']['chain'] = 'field:label:error:email'
form_field_definitions.user['mail']['required'] = False
form_field_definitions.user['mail']['protected'] = False

# user userPassword
form_field_definitions.user['userPassword'] = dict()
form_field_definitions.user['userPassword']['chain'] = \
    'field:label:error:password'
form_field_definitions.user['userPassword']['props'] = dict()
form_field_definitions.user['userPassword']['props']['minlength'] = 6
form_field_definitions.user['userPassword']['props']['ascii'] = True
form_field_definitions.user['userPassword']['required'] = True
form_field_definitions.user['userPassword']['protected'] = False

# group default
form_field_definitions.group['default'] = form_field_definitions.user['default']

# group id
form_field_definitions.group['id'] = form_field_definitions.user['id']