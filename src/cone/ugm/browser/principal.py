from cone.app import compat
from cone.app.browser.utils import make_url
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
from yafowil.base import factory
from yafowil.base import UNSET


_ = TranslationStringFactory('cone.ugm')


def default_form_field_factory(model, label, value):
    """Default form field factory.

    A form field factory is a callable which gets passed the application model
    node instance, a label and the preset value of a form field, and returns a
    widget created by the yafowil factory.

    The default factory creates a simple text field with no validation
    or whatsoever.

    :param model: The application model node instance.
    :param label: The form field label.
    :param value: The field preset value.
    :return: ``yafowil.base.Widget`` instance created by
        ``yafowil.base.factory``.
    """
    return factory(
        'field:label:text',
        value=value,
        props={
            'label': label
        })


class FormFieldFactoryProxy(object):
    """Proxy object for form field factories.

    Provides a ``__call__`` function which acts as proxy for the concrete
    form field factory callable. Additionally holds ``attr`` attribute,
    which defines the target attribute name of the principal node.
    """

    def __init__(self, factory, attr):
        """Create form field factory proxy.

        :param factory: The form field factory proxy callable.
        :param attr: The target attribute name on the principal node.
        """
        self.factory = factory
        self.attr = attr

    def __call__(self, model, label, value):
        """Call proxied form field factory proxy callable.

        :param model: The application model node instance.
        :param label: The form field label.
        :param value: The field preset value.
        :return: ``yafowil.base.Widget`` instance created by
            ``yafowil.base.factory``.
        """
        return self.factory(model, label, value)


SCOPE_USER = 'user'
SCOPE_GROUP = 'group'
BACKEND_ALL = '__all_backends__'


class _form_field(object):
    """Abstract form field factory registry and decorator.
    """

    scope = None
    """Registration scope."""

    registry = dict(
        SCOPE_USER={},
        SCOPE_GROUP={}
    )
    """Form field factory and attribute name registry by scope and UGM backend
    name.
    """

    def __init__(self, field, attr=None, backend=BACKEND_ALL):
        """Initialize decorator by attribute name and backend name.

        :param field: The form field name.
        :param attr: The target attribute name on the principal node.
        :param backend: UGM backend name the form field factory is valid for.
        """
        assert self.scope
        self.field = field
        self.attr = attr
        self.backend = backend

    def __call__(self, factory):
        """Decorator call. Register the form field factory.

        :param factory: The form field factory callable.
        :return: The form field factory callable.
        """
        scope_reg = self.registry[self.scope]
        backend_reg = scope_reg.setdefault(self.backend, {})
        backend_reg[self.field] = (factory, self.attr)
        return factory

    @classmethod
    def factory(cls, field, backend=BACKEND_ALL):
        """Lookup form field factory by field name and backend name.

        :param field: The form field name.
        :param backend: UGM backend name the form field factory is valid for.
        :return: ``FormFieldFactoryProxy`` wrapping the principal node attribute
            name and the form field factory callable.
        """
        assert cls.scope
        scope_reg = cls.registry[cls.scope]
        for backend_name in (backend, BACKEND_ALL):
            backend_reg = scope_reg.setdefault(backend_name, {})
            entry = backend_reg.get(field)
            if entry:
                return FormFieldFactoryProxy(*entry)
        FormFieldFactoryProxy(default_form_field_factory, None)


class user_field(_form_field):
    """Form field factory registry and decorator for user principal form.
    """
    scope = SCOPE_USER


class group_field(_form_field):
    """Form field factory registry and decorator for group principal form.
    """
    scope = SCOPE_GROUP


class PrincipalForm(object):

    form_name = None

    @property
    def form_attrmap(self):
        raise NotImplementedError(u"Abstract principal form does not provide "
                                  u"``form_attrmap``")

    @property
    def form_field_definitions(self):
        raise NotImplementedError(u"Abstract principal form does not provide "
                                  u"``form_field_definitions``")

    def prepare(self):
        resource = self.action_resource

        # load props befor edit form is rendered.
        # XXX: this is LDAP world, not generic UGM
        if resource == 'edit':
            self.model.attrs.context.load()

        action = make_url(self.request, node=self.model, resource=resource)
        form = factory(
            u'form',
            name=self.form_name,
            props={
                'action': action,
            })
        attrmap = self.form_attrmap
        if not attrmap:
            return form
        schema = self.form_field_definitions
        default = schema['default']
        localizer = get_localizer(self.request)
        for key, val in attrmap.items():
            field = schema.get(key, default)
            chain = field.get('chain', default['chain'])
            props = dict()
            props['label'] = _(val, default=val)
            if field.get('required'):
                req = _(
                    'no_field_value_defined',
                    default='No ${field} defined',
                    mapping={
                        'field': localizer.translate(_(val, default=val))
                    }
                )
                props['required'] = req
            props.update(field.get('props', dict()))
            value = UNSET
            mode = 'edit'
            if resource == 'edit':
                if field.get('protected'):
                    mode = 'display'
                value = self.model.attrs.get(key, u'')
            custom = field.get('custom', dict())
            custom_parsed = dict()
            if custom.keys():
                for k, v in custom.items():
                    val_parsed = list()
                    for c_chain in v:
                        chain_parsed = list()
                        for part in c_chain:
                            if isinstance(part, compat.STR_TYPE):
                                if not part.startswith('context.'):
                                    msg = 'chain callable definition invalid'
                                    raise Exception(msg)
                                attrname = part[part.index('.') + 1:]
                                clb = getattr(self, attrname)
                            else:
                                clb = part
                            chain_parsed.append(clb)
                        val_parsed.append(chain_parsed)
                    custom_parsed[k] = tuple(val_parsed)
            form[key] = factory(
                chain,
                value=value,
                props=props,
                custom=custom_parsed,
                mode=mode)
        form['save'] = factory(
            'submit',
            props={
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
                'label': _('save', default='Save'),
            })
        if resource == 'add':
            form['cancel'] = factory(
                'submit',
                props={
                    'action': 'cancel',
                    'expression': True,
                    'handler': None,
                    'next': self.next,
                    'label': _('cancel', default='Cancel'),
                    'skip': True,
                })
        self.form = form
