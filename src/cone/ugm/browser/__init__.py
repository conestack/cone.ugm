from cone.app.model import Properties
from pyramid.static import static_view
from yafowil.base import factory
from yafowil.common import ascii_extractor


static_resources = static_view('static', use_subpath=True)


def default_form_field_factory(context, label, value):
    """Default form field factory.

    A form field factory is a callable which gets passed the form tile instance
    as context, a label and the preset value of a form field, and returns a
    widget created by the yafowil factory.

    The default factory creates a simple text field with no validation
    or whatsoever.

    :param context: The form tile instance.
    :param label: The form field label.
    :param value: The field preset value.
    :return: ``yafowil.base.Widget`` instance created by ``yafowil.base.factory``
    """
    return factory(
        'field:label:text',
        value=value,
        props={
            'label': label
        })


SCOPE_USER = 'user'
SCOPE_GROUP = 'group'
BACKEND_ALL = '__all_backends__'


class _form_field(object):
    """Abstract base class for form field factory decorators.
    """
    scope = None
    registry = dict(
        SCOPE_USER={},
        SCOPE_GROUP={}
    )

    def __init__(self, field_name, backend_name=BACKEND_ALL, attr_name=None):
        self.field_name = field_name
        self.backend_name = backend_name
        self.attr_name = attr_name

    def __call__(self, ob):
        scope_reg = self.registry[self.scope]
        backend_reg = scope_reg.setdefault(self.backend_name, {})
        backend_reg[self.field_name] = dict(
            callback=ob,
            attr_name=self.attr_name
        )
        return ob

    @classmethod
    def factory(cls, field_name, backend_name, value):
        scope_reg = cls.registry[cls.scope]
        for b_name in (backend_name, BACKEND_ALL):
            backend_reg = scope_reg.setdefault(b_name, {})
            factory = backend_reg.get(field_name)
            if factory:
                return factory
        return default_form_field_factory


class user_field(_form_field):
    scope = SCOPE_USER


class group_field(_form_field):
    scope = SCOPE_GROUP


###############################################################################
# XXX: get rid of below
###############################################################################

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
