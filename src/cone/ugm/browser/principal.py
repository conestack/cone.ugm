from yafowil.base import (
    factory,
    UNSET,
)
from cone.app.browser.utils import make_url

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
        for key, val in attrmap.items():
            field = schema.get(key, default)
            chain = field.get('chain', default['chain'])
            props = dict()
            props['label'] = val
            if field.get('required'):
                props['required'] = 'No %s defined' % val
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
                                callable = getattr(self, attrname)
                            else:
                                callable = part
                            chain_parsed.append(callable)
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
            props = {
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
                'label': 'Save',
            })
        if resource =='add':
            form['cancel'] = factory(
                'submit',
                props = {
                    'action': 'cancel',
                    'expression': True,
                    'handler': None,
                    'next': self.next,
                    'label': 'Cancel',
                    'skip': True,
                })
        self.form = form