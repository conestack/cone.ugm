from cone.app.browser.utils import make_url
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from yafowil.base import UNSET
from yafowil.base import factory


_ = TranslationStringFactory('cone.ugm')


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
                            if isinstance(part, basestring):
                                if not part.startswith('context.'):
                                    raise Exception(
                                        u"chain callable definition invalid")
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
