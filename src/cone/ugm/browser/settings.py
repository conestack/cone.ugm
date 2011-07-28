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
    YAMLForm,
)
from cone.app.browser.settings import SettingsPart
from cone.ugm.model.settings import (
    ServerSettings,
    UsersSettings,
    GroupsSettings,
    RolesSettings,
)
from cone.ugm.model.utils import (
    ugm_server,
    ugm_users,
    ugm_groups,
    ugm_roles,
)


class VocabMixin(object):

    scope_vocab = [
        (str(BASE), 'BASE'),
        (str(ONELEVEL), 'ONELEVEL'),
        (str(SUBTREE), 'SUBTREE'),
    ]


@tile('content', 'templates/server_settings.pt',
      interface=ServerSettings, permission='manage', strict=False)
class ServerSettingsTile(ProtectedContentTile):
    
    @property
    def ldap_status(self):
        if self.model.ldap_connectivity:
            return 'OK'
        return 'Down'


@tile('editform', interface=ServerSettings, permission="manage")
class ServerSettingsForm(Form):
    __metaclass__ = plumber
    __plumbing__ = SettingsPart, YAMLForm
    
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/server_settings.yaml'
    
    def save(self, widget, data):
        model = self.model
        for attr_name in ['uri', 'user']:
            val = data.fetch('settings.%s' % attr_name).extracted
            setattr(model.attrs, attr_name, val)
        password = data.fetch('settings.password').extracted
        if password is not UNSET:
            setattr(model.attrs, 'password', password)
        model()
        model.invalidate()


@tile('content', 'templates/users_settings.pt',
      interface=UsersSettings, permission='manage', strict=False)
class UsersSettingsTile(ProtectedContentTile):
    
    @property
    def ldap_users(self):
        if self.model.ldap_users_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('editform', interface=UsersSettings, permission="manage")
class UsersSettingsForm(Form, VocabMixin):
    __metaclass__ = plumber
    __plumbing__ = SettingsPart, YAMLForm
    
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/users_settings.yaml'
    
    # XXX: read from column config
    sort_column_vocab = [
        ('col_1', 'col_1'),
        ('col_2', 'col_2'),
        ('col_3', 'col_3'),
    ]
    
    @property
    def users_aliases_attrmap(self):
        attrs = self.model.attrs
        users_aliases_attrmap = odict()
        users_aliases_attrmap['rdn'] = attrs.users_aliases_attrmap.get('rdn')
        users_aliases_attrmap['id'] = attrs.users_aliases_attrmap.get('id')
        users_aliases_attrmap['login'] = \
            attrs.users_aliases_attrmap.get('login')
        return users_aliases_attrmap
    
    @property
    def users_listing_columns(self):
        attrs = self.model.attrs
        users_listing_columns = odict()
        key_1 = attrs.users_listing_columns.get('col_1', 'cn:Fullname')
        key_2 = attrs.users_listing_columns.get('col_2', 'sn:Surname')
        key_3 = attrs.users_listing_columns.get('col_3', 'mail:Email')
        users_listing_columns['col_1'] = key_1
        users_listing_columns['col_2'] = key_2
        users_listing_columns['col_3'] = key_3
        return users_listing_columns
    
    @property
    def users_listing_default_column(self):
        attrs = self.model.attrs
        users_listing_default_column = attrs.users_listing_default_column
        if not users_listing_default_column:
            users_listing_default_column = 'col_1'
        return users_listing_default_column
    
    def save(self, widget, data):
        model = self.model
        for attr_name in ['users_dn',
                          'users_scope',
                          'users_query',
                          'users_object_classes',
                          'users_aliases_attrmap',
                          'users_form_attrmap',
                          'users_listing_columns',
                          'users_listing_default_column']:
            val = data.fetch('settings.%s' % attr_name).extracted
            if attr_name == 'users_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()


@tile('content', 'templates/groups_settings.pt',
      interface=GroupsSettings, permission='manage', strict=False)
class GroupsSettingsTile(ProtectedContentTile):
    
    @property
    def ldap_groups(self):
        if self.model.ldap_groups_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('editform', interface=GroupsSettings, permission="manage")
class GroupsSettingsForm(Form, VocabMixin):
    __metaclass__ = plumber
    __plumbing__ = SettingsPart, YAMLForm
    
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/groups_settings.yaml'
    
    # XXX: read from column config
    sort_column_vocab = [
        ('col_1', 'col_1'),
    ]
    
    @property
    def groups_aliases_attrmap(self):
        attrs = self.model.attrs
        groups_aliases_attrmap = odict()
        groups_aliases_attrmap['rdn'] = attrs.groups_aliases_attrmap.get('rdn')
        groups_aliases_attrmap['id'] = attrs.groups_aliases_attrmap.get('id')
        return groups_aliases_attrmap
    
    @property
    def groups_listing_columns(self):
        attrs = self.model.attrs
        groups_listing_columns = odict()
        key_1 = attrs.groups_listing_columns.get('col_1', 'id:Groupname')
        groups_listing_columns['col_1'] = key_1
        return groups_listing_columns
    
    @property
    def groups_listing_default_column(self):
        attrs = self.model.attrs
        groups_listing_default_column = attrs.groups_listing_default_column
        if not groups_listing_default_column:
            groups_listing_default_column = 'col_1'
        return groups_listing_default_column
    
    def save(self, widget, data):
        model = self.model
        for attr_name in ['groups_dn',
                          'groups_scope',
                          'groups_query',
                          'groups_object_classes',
                          'groups_aliases_attrmap',
                          'groups_form_attrmap',
                          #'groups_relation',
                          'groups_listing_columns',
                          'groups_listing_default_column']:
            val = data.fetch('settings.%s' % attr_name).extracted
            if attr_name == 'groups_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()


@tile('content', 'templates/roles_settings.pt',
      interface=RolesSettings, permission='manage', strict=False)
class RolesSettingsTile(ProtectedContentTile):
    
    @property
    def ldap_roles(self):
        if self.model.ldap_roles_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('editform', interface=RolesSettings, permission="manage")
class RolesSettingsForm(Form, VocabMixin):
    __metaclass__ = plumber
    __plumbing__ = SettingsPart, YAMLForm
    
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/roles_settings.yaml'
    
    @property
    def roles_aliases_attrmap(self):
        attrs = self.model.attrs
        roles_aliases_attrmap = odict()
        roles_aliases_attrmap['rdn'] = attrs.roles_aliases_attrmap.get('rdn')
        roles_aliases_attrmap['id'] = attrs.roles_aliases_attrmap.get('id')
        return roles_aliases_attrmap
    
    def save(self, widget, data):
        model = self.model
        for attr_name in ['roles_dn',
                          'roles_scope',
                          'roles_query',
                          'roles_object_classes',
                          'roles_aliases_attrmap',
                          'roles_form_attrmap',
                          #'roles_relation',
                          ]:
            val = data.fetch('settings.%s' % attr_name).extracted
            if attr_name == 'roles_object_classes':
                val = [v.strip() for v in val.split(',') if v.strip()]
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
