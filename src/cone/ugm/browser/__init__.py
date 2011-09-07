from pyramid.static import static_view
from yafowil.common import ascii_extractor
from cone.app.model import Properties


static_resources = static_view('static', use_subpath=True)


# user and group form field definitions for yafowil
# overwrite or extend in integration __init__
# XXX: future -> yafowil form field properties editor
# XXX: far future -> yafowil JS form editor
# XXX: user and group form schema definitions should then be resolved in order
#      yafowil browser based cfg -> default cfg -> general default
form_field_definitions = Properties()
form_field_definitions.user = dict()
form_field_definitions.group = dict()
_user = form_field_definitions.user
_group = form_field_definitions.group


_user['default'] = dict()
_user['default']['chain'] = 'field:label:error:text'
_user['default']['required'] = False
_user['default']['protected'] = False


_user['id'] = dict()
_user['id']['chain'] = 'field:*ascii:*exists:label:error:text'
_user['id']['props'] = dict()
_user['id']['props']['ascii'] = True
_user['id']['custom'] = dict()
_user['id']['custom']['ascii'] = ([ascii_extractor], [], [], [], [])
_user['id']['custom']['exists'] = (['context.exists'], [], [], [], [])
_user['id']['required'] = True
_user['id']['protected'] = True


_user['mail'] = dict()
_user['mail']['chain'] = 'field:label:error:email'
_user['mail']['required'] = False
_user['mail']['protected'] = False


_user['userPassword'] = dict()
_user['userPassword']['chain'] = 'field:label:error:password'
_user['userPassword']['props'] = dict()
_user['userPassword']['props']['minlength'] = 6
_user['userPassword']['props']['ascii'] = True
_user['userPassword']['required'] = True
_user['userPassword']['protected'] = False


_user['cn'] = dict()
_user['cn']['chain'] = 'field:label:error:text'
_user['cn']['required'] = True
_user['cn']['protected'] = False


_user['sn'] = dict()
_user['sn']['chain'] = 'field:label:error:text'
_user['sn']['required'] = True
_user['sn']['protected'] = False


_group['default'] = _user['default']


_group['id'] = _user['id']