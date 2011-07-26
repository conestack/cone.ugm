import os
import ldap
import cone.ugm
from node.utils import instance_property
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
from cone.ugm.model.utils import APP_PATH


def _invalidate_ugm_settings(model):
    settings = model.parent
    settings['ugm_server']._ldap_props = None
    settings['ugm_users']._ldap_ucfg = None
    settings['ugm_groups']._ldap_gcfg = None
    import cone.ugm
    cone.ugm.backend = None


ugm_config = None
ugm_config_path = os.path.join(APP_PATH, 'etc', 'ldap.xml')

def _get_ugm_config():
    from cone.ugm.model import settings
    if settings.ugm_config is not None:
        return settings.ugm_config
    settings.ugm_config = XMLProperties(settings.ugm_config_path)
    return settings.ugm_config


class UgmSettings(BaseNode):
    
    def __call__(self):
        self.attrs()
    
    def invalidate(self):
        _invalidate_ugm_settings(self)

    @property
    def attrs(self):
        return self._config
    
    @property
    def _config(self):
        return _get_ugm_config()


class ServerSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "LDAP Props"
        metadata.description = "LDAP properties"
        return metadata
    
    @property
    def ldap_connectivity(self):
        return testLDAPConnectivity(props=self.ldap_props)
    
    @property
    def ldap_props(self):
        if not hasattr(self, '_ldap_props') or self._ldap_props is None:
            config = self._config
            self._ldap_props = LDAPProps(
                uri=config.uri,
                user=config.user,
                password=config.password)
        return self._ldap_props


class UsersSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Users Settings"
        metadata.description = "LDAP users settings"
        return metadata
    
    @property
    def ldap_users_container_valid(self):
        try:
            node = queryNode(
                self.parent['ugm_server'].ldap_props, self._config.users_dn)
            return bool(node)
        except ldap.LDAPError:
            return False
    
    @property
    def ldap_ucfg(self):
        if not hasattr(self, '_ldap_ucfg') or self._ldap_ucfg is None:
            config = self._config
            map = dict()
            for key in config.users_aliases_attrmap.keys():
                map[key] = config.users_aliases_attrmap[key]
            for key in config.users_form_attrmap.keys():
                if key in ['id', 'login']:
                    continue
                map[key] = key
            import cone.ugm.model
            self._ldap_ucfg = LDAPUsersConfig(
                baseDN=config.users_dn,
                attrmap=map,
                scope=int(config.users_scope),
                queryFilter=config.users_query,
                objectClasses=config.users_object_classes,
                defaults=cone.ugm.model.factory_defaults.user)
        return self._ldap_ucfg


class GroupsSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups Settings"
        metadata.description = "LDAP groups settings"
        return metadata
    
    @property
    def ldap_groups_container_valid(self):
        try:
            node = queryNode(
                self.parent['ugm_server'].ldap_props, self._config.groups_dn)
            return bool(node)
        except ldap.LDAPError:
            return False
    
    @property
    def ldap_gcfg(self):
        if not hasattr(self, '_ldap_gcfg') or self._ldap_gcfg is None:
            config = self._config
            map = dict()
            for key in config.groups_aliases_attrmap.keys():
                map[key] = config.groups_aliases_attrmap[key]
            for key in config.groups_form_attrmap.keys():
                if key in ['id']:
                    continue
                map[key] = key
            import cone.ugm.model
            self._ldap_gcfg = LDAPGroupsConfig(
                baseDN=config.groups_dn,
                attrmap=map,
                scope=int(config.groups_scope),
                queryFilter=config.groups_query,
                objectClasses=config.groups_object_classes,
                #member_relation=config.groups_relation,
                defaults=cone.ugm.model.factory_defaults.group,
                )
        return self._ldap_gcfg

# XXX: later
#class RolesSettings(BaseNode):
#    
#    @instance_property
#    def metadata(self):
#        metadata = BaseMetadata()
#        metadata.title = "Roles Settings"
#        metadata.description = "LDAP roles settings"
#        return metadata
#    
#    @property
#    def ldap_rcfg(self):
#        # XXX: later
#        return None
