from plumber import plumber
from odict import odict
from node.ext.ldap.scope import (
    BASE,
    ONELEVEL,
    SUBTREE,
)
from yafowil.base import (
    factory,
    UNSET,
)
from cone.tile import tile
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.form import (
    Form,
    EditPart,
)
from cone.ugm.model.interfaces import ISettings


scope_vocab = [
    (str(BASE), 'BASE'),
    (str(ONELEVEL), 'ONELEVEL'),
    (str(SUBTREE), 'SUBTREE'),
]


@tile('content', 'templates/settings.pt', interface=ISettings,
      permission='login', strict=False)
class Settings(ProtectedContentTile):
    
    @property
    def ldap_status(self):
        if self.model.ldap_connectivity == 'success':
            return 'OK'
        return 'Down'
    
    @property
    def ldap_users(self):
        if self.model.ldap_users_container_valid:
            return 'OK'
        return 'Inexistent'
        
    @property
    def ldap_groups(self):
        if self.model.ldap_groups_container_valid:
            return 'OK'
        return 'Inexistent'
    
    def scope(self, scope):
        for term in scope_vocab:
            if term[0] == scope:
                return term[1]
        return ''


@tile('editform', interface=ISettings, permission="view")
class LDAPSettingsForm(Form):
    __metaclass__ = plumber
    __plumbing__ = EditPart
    
    def prepare(self):
        model = self.model
        form = factory(u'form',
                       name='editform',
                       props={'action': '%s/edit' % self.nodeurl})
        form['uri'] = factory(
            'field:label:error:text',
            value = model.attrs.uri,
            props = {
                'required': 'No URI defined',
                'label': 'LDAP URI',
            })
        form['user'] = factory(
            'field:label:error:text',
            value = model.attrs.user,
            props = {
                'required': 'No user defined',
                'label': 'LDAP Manager User',
            })
        form['password'] = factory(
            'field:label:error:password',
            value = model.attrs.password,
            props = {
                'required': 'No password defined',
                'label': 'LDAP Manager Password',
            })
        form['users_dn'] = factory(
            'field:label:error:text',
            value = model.attrs.users_dn,
            props = {
                'required': 'No Users DN defined',
                'label': 'Users Base DN',
            })
        form['users_scope'] = factory(
            'field:label:select',
            value = model.attrs.users_scope,
            props = {
                'label': 'Users scope',
                'vocabulary': scope_vocab,
            })
        form['users_query'] = factory(
            'field:label:text',
            value = model.attrs.users_query,
            props = {
                'label': 'Users query',
            })
        form['users_object_classes'] = factory(
            'field:label:text',
            value = u', '.join(model.attrs.get('users_object_classes', [])),
            props = {
                'label': 'Users object classes',
            })
        users_attrmap = odict()
        users_attrmap['rdn'] = model.attrs.users_attrmap.get('rdn')
        users_attrmap['id'] = model.attrs.users_attrmap.get('id')
        users_attrmap['login'] = model.attrs.users_attrmap.get('login')
        form['users_attrmap'] = factory(
            'field:label:error:dict',
            value = users_attrmap,
            props = {
                'required': 'User attribute mapping values are mandatory',
                'label': 'User attribute mapping',
                'static': True,
                'head': {
                    'key': 'Reserved key',
                    'value': 'LDAP attr name',
                }
            })
        form['users_form_attrmap'] = factory(
            'field:label:dict',
            value = model.attrs.users_form_attrmap,
            props = {
                'label': 'User form attribute mapping',
                'head': {
                    'key': 'LDAP attr name',
                    'value': 'Form label',
                }
            })
        form['groups_dn'] = factory(
            'field:label:error:text',
            value = model.attrs.groups_dn,
            props = {
                'required': 'No Groups DN defined',
                'label': 'Groups Base DN',
            })
        form['groups_scope'] = factory(
            'field:label:select',
            value = model.attrs.groups_scope,
            props = {
                'label': 'Groups scope',
                'vocabulary': scope_vocab,
            })
        form['groups_query'] = factory(
            'field:label:text',
            value = model.attrs.groups_query,
            props = {
                'label': 'Groups query',
            })
        form['groups_object_classes'] = factory(
            'field:label:text',
            value = u', '.join(model.attrs.get('groups_object_classes', [])),
            props = {
                'label': 'Groups object classes',
            })
        form['groups_relationship'] = factory(
            'field:label:text',
            value = model.attrs.groups_relationship,
            props = {
                'label': 'Group Relationship',
            })
        form['save'] = factory(
            'submit',
            props = {
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
                'label': 'Save',
            })
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
    
    def save(self, widget, data):
        model = self.model
        for attr_name in ['uri', 'user', 'users_dn', 'users_scope',
                          'users_query', 'users_object_classes',
                          'users_attrmap', 'users_form_attrmap',
                          'groups_dn', 'groups_scope', 'groups_query',
                          'groups_object_classes', 'groups_relationship']:
            val = data.fetch('editform.%s' % attr_name).extracted
            if attr_name in ['users_object_classes', 'groups_object_classes']:
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        password = data.fetch('editform.password').extracted
        if password is not UNSET:
            setattr(model.attrs, 'password', password)
        model()
        model.invalidate()