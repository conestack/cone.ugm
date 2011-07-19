import os
import ldap
from zope.interface import implements
from node.ext.ldap import LDAPProps
from node.ext.ldap.base import testLDAPConnectivity
from node.ext.ldap._node import queryNode
from node.ext.ldap.ugm import UsersConfig as LDAPUsersConfig
from node.ext.ldap.ugm import GroupsConfig as LDAPGroupsConfig
from cone.app.model import (
    BaseNode,
    XMLProperties,
    BaseMetadata,
)
from cone.ugm.model.interfaces import ISettings
from cone.ugm.model.utils import APP_PATH


class UgmSettings(BaseNode):

    implements(ISettings)

    def __init__(self, name=None, _app_path=None):
        """``_app_path`` defines an alternative path for app root and is
        for testing purposes only
        """
        BaseNode.__init__(self, name)
        self._file_path = os.path.join(_app_path or APP_PATH, 'etc', 'ldap.xml')
        self._config = XMLProperties(self._file_path)
        self.invalidate()

    def __call__(self):
        self.attrs()

    @property
    def attrs(self):
        return self._config

    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "LDAP Settings"
        metadata.description = "LDAP Connection Settings"
        return metadata

    def invalidate(self):
        self._ldap_props = None
        self._ldap_ucfg = None
        self._ldap_gcfg = None
        if self.parent:
            import cone.ugm
            cone.ugm.backend = None

    @property
    def ldap_connectivity(self):
        return testLDAPConnectivity(props=self.ldap_props)

    @property
    def ldap_users_container_valid(self):
        try:
            queryNode(self.ldap_props, self._config.users_dn)
            return True
        except ldap.LDAPError, e:
            return False

    @property
    def ldap_groups_container_valid(self):
        try:
            queryNode(self.ldap_props, self._config.groups_dn)
            return True
        except ldap.LDAPError, e:
            return False

    @property
    def ldap_props(self):
        if self._ldap_props is None:
            config = self._config
            self._ldap_props = LDAPProps(uri=config.uri,
                                         user=config.user,
                                         password=config.password)
        return self._ldap_props

    @property
    def ldap_ucfg(self):
        if self._ldap_ucfg is None:
            config = self._config
            map = dict()
            for key in config.users_attrmap.keys():
                map[key] = config.users_attrmap[key]
            for key in config.users_form_attrmap.keys():
                if key in ['id', 'login']:
                    continue
                map[key] = key
            self._ldap_ucfg = LDAPUsersConfig(
                baseDN=config.users_dn,
                attrmap=map,
                scope=int(config.users_scope),
                queryFilter=config.users_query,
                objectClasses=config.users_object_classes)
        return self._ldap_ucfg

    @property
    def ldap_gcfg(self):
        if self._ldap_gcfg is None:
            config = self._config
            map = dict()
            # XXX: each criteria is expected in attrmap. is this what we want?
            self._ldap_gcfg = LDAPGroupsConfig(
                baseDN=config.groups_dn,
                # XXX: from config
                attrmap={
                    'id': 'cn',
                    'rdn': 'cn',
                    'cn': 'cn',
                    'member': 'member',
                    'uniqueMember': 'uniqueMember',
                },
                scope=int(config.groups_scope),
                queryFilter=config.groups_query,
                objectClasses=config.groups_object_classes,
                member_relation=config.groups_relation,
                )
        return self._ldap_gcfg
    
    @property
    def ldap_rcfg(self):
        # XXX: later
        return None
