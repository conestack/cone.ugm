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
from cone.app.browser.form import Form
from cone.app.browser.settings import SettingsPart
from cone.ugm.model.settings import UgmSettings


scope_vocab = [
    (str(BASE), 'BASE'),
    (str(ONELEVEL), 'ONELEVEL'),
    (str(SUBTREE), 'SUBTREE'),
]

sort_column_vocab = [
    ('col_1', 'col_1'),
    ('col_2', 'col_2'),
    ('col_2', 'col_2'),
]


@tile('content', 'templates/settings.pt', interface=UgmSettings,
      permission='manage', strict=False)
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


@tile('editform', interface=UgmSettings, permission='manage')
class LDAPSettingsForm(Form):
    __metaclass__ = plumber
    __plumbing__ = SettingsPart

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
        users_listing_columns = odict()
        key_1 = model.attrs.users_listing_columns.get('col_1', 'cn:Fullname')
        key_2 = model.attrs.users_listing_columns.get('col_2', 'sn:Surname')
        key_3 = model.attrs.users_listing_columns.get('col_3', 'mail:Email')
        users_listing_columns['col_1'] = key_1
        users_listing_columns['col_2'] = key_2
        users_listing_columns['col_3'] = key_3
        form['users_listing_columns'] = factory(
            'field:label:dict',
            value = users_listing_columns,
            props = {
                'required': 'Column configuration for user listings values ' +\
                            'are mandatory',
                'label': 'Column configuration for user listings',
                'static': True,
                'head': {
                    'key': 'Listing column',
                    'value': 'LDAP Attribute',
                }
            })
        users_listing_default_column = model.attrs.users_listing_default_column
        if not users_listing_default_column:
            users_listing_default_column = 'col_1'
        form['users_listing_default_column'] = factory(
            'field:label:select',
            value = users_listing_default_column,
            props = {
                'label': 'Users listing default columns',
                'vocabulary': sort_column_vocab,
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
        form['groups_relation'] = factory(
            'field:label:text',
            value = model.attrs.groups_relation,
            props = {
                'label': 'Group-member-relation',
            })
        groups_listing_columns = odict()
        key_1 = model.attrs.groups_listing_columns.get('col_1', 'cn:Groupname')
        groups_listing_columns['col_1'] = key_1
        form['groups_listing_columns'] = factory(
            'field:label:dict',
            value = groups_listing_columns,
            props = {
                'required': 'Column configuration for group listings value ' +\
                            'is mandatory',
                'label': 'Column configuration for groups listings',
                'static': True,
                'head': {
                    'key': 'Listing Column',
                    'value': 'LDAP Attribute',
                }
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
        self.form = form

    def save(self, widget, data):
        model = self.model
        for attr_name in ['uri',
                          'user',
                          'users_dn',
                          'users_scope',
                          'users_query',
                          'users_object_classes',
                          'users_attrmap',
                          'users_form_attrmap',
                          'users_listing_columns',
                          'users_listing_default_column',
                          'groups_dn',
                          'groups_scope',
                          'groups_query',
                          'groups_object_classes',
                          'groups_relation',
                          'groups_listing_columns']:
            val = data.fetch('editform.%s' % attr_name).extracted
            if attr_name in ['users_object_classes', 'groups_object_classes']:
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        password = data.fetch('editform.password').extracted
        if password is not UNSET:
            setattr(model.attrs, 'password', password)
        model()
        model.invalidate()
