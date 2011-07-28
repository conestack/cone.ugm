from plumber import plumber
from odict import odict
from ldap.functions import explode_dn
from node.ext.ldap import (
    BASE,
    ONELEVEL,
    SUBTREE,
    queryNode,
    LDAPNode,
)
from yafowil.base import (
    factory,
    UNSET,
)
from cone.tile import (
    tile,
    Tile,
)
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.form import (
    Form,
    YAMLForm,
)
from cone.app.browser.settings import SettingsPart
from cone.app.browser.ajax import (
    ajax_continue,
    ajax_message,
    AjaxAction,
)
from cone.app.browser.utils import (
    make_url,
    make_query,
)
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


def encode_dn(dn):
    return dn.replace('=', '%%')


def decode_dn(dn):
    return dn.replace('%%', '=')


class CreateContainerTrigger(Tile):
    
    @property
    def creation_dn(self):
        raise NotImplementedError(u"Abstract ``CreateContainerTrigger`` "
                                  u"doe not implement ``creation_dn``")
    
    @property
    def creation_target(self):
        dn = encode_dn(self.creation_dn)
        query = make_query(dn=dn)
        return make_url(self.request, node=self.model, query=query)
    
    @property
    def ldap_connectivity(self):
        return self.model.parent['ugm_server'].ldap_connectivity


class CreateContainerAction(Tile):
    
    @property
    def continuation(self):
        raise NotImplementedError(u"Abstract ``CreateContainerAction`` "
                                  u"doe not implement ``continuation``")
    
    def render(self):
        try:
            message = self.create_container()
            ajax_message(self.request, message, 'info')
            continuation = self.continuation
            ajax_continue(self.request, continuation)
        except Exception, e:
            message = u"Cannor create container %s" % str(e)
            ajax_message(self.request, message, 'error')
        return u''
    
    def create_container(self):
        dn = decode_dn(self.request.params.get('dn', ''))
        if not dn:
            raise Exception(u"No container DN defined.")
        if not dn.startswith('ou='):
            raise Exception(u"Expected 'ou' as RDN Attribute.")
        props = self.model.parent['ugm_server'].ldap_props
        try:
            parent_dn = ','.join(explode_dn(dn)[1:])
        except Exception:
            raise Exception(u"Invalid DN.")
        rdn = explode_dn(dn)[0]
        node = queryNode(props, parent_dn)
        if node is None:
            raise Exception(u"Parent not found. Cannot continue.")
        node[rdn] = LDAPNode()
        node[rdn].attrs['objectClass'] = ['organizationalUnit']
        node()
        return u"Created '%s'" % rdn


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
class UsersSettingsTile(ProtectedContentTile, CreateContainerTrigger):
    
    @property
    def creation_dn(self):
        return self.model.attrs.users_dn
    
    @property
    def ldap_users(self):
        if self.model.ldap_users_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('create_container', interface=UsersSettings, permission='manage')
class UsersCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ugm_users')


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
class GroupsSettingsTile(ProtectedContentTile, CreateContainerTrigger):
    
    @property
    def creation_dn(self):
        return self.model.attrs.groups_dn
    
    @property
    def ldap_groups(self):
        if self.model.ldap_groups_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('create_container', interface=GroupsSettings, permission='manage')
class GroupsCreateContainerAction(CreateContainerAction):
    
    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ugm_groups')


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
class RolesSettingsTile(ProtectedContentTile, CreateContainerTrigger):
    
    @property
    def creation_dn(self):
        return self.model.attrs.roles_dn
    
    @property
    def ldap_roles(self):
        if self.model.ldap_roles_container_valid:
            return 'OK'
        return 'Inexistent'


@tile('create_container', interface=RolesSettings, permission='manage')
class RolesCreateContainerAction(CreateContainerAction):

    @property
    def continuation(self):
        url = make_url(self.request, node=self.model)
        return AjaxAction(url, 'content', 'inner', '.ugm_roles')


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