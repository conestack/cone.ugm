import os
import ldap
import cone.ugm
from node.utils import instance_property
from node.ext.ldap import (
    LDAPProps,
    LDAPNode,
    testLDAPConnectivity,
)
from node.ext.ldap.ugm import (
    UsersConfig as LDAPUsersConfig,
    GroupsConfig as LDAPGroupsConfig,
    RolesConfig as LDAPRolesConfig,
)
from node.ext.ldap.ugm._api import EXPIRATION_DAYS
from cone.app.model import (
    BaseNode,
    XMLProperties,
    BaseMetadata,
)
from cone.ugm.model.utils import ldap_cfg_file


def _read_ugm_config():
    cfg_file = ldap_cfg_file()
    if not os.path.isfile(cfg_file):
        raise ValueError('Configuration file %s does not exist.'% cfg_file)
    ugm_config = XMLProperties(cfg_file)
    return ugm_config


def _invalidate_ugm_settings(model):
    settings = model.root['settings']
    settings['ugm_server']._ldap_props = None
    settings['ugm_server']._xml_config = None
    settings['ugm_users']._ldap_ucfg = None
    settings['ugm_users']._xml_config = None
    settings['ugm_groups']._ldap_gcfg = None
    settings['ugm_groups']._xml_config = None
    import cone.app
    cone.app.cfg.auth = None


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
        if not hasattr(self, '_xml_config') or self._xml_config is None:
            self._xml_config = _read_ugm_config()
        return self._xml_config


class GeneralSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "UGM Settings"
        metadata.description = "General user and group management settings"
        return metadata


class ServerSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "LDAP Props"
        metadata.description = "LDAP properties"
        return metadata
    
    @property
    def ldap_connectivity(self):
        try:
            props = self.ldap_props
        except ValueError:
            return False
        return testLDAPConnectivity(props=props) == 'success'    
    
    @property
    def ldap_props(self):
        if not hasattr(self, '_ldap_props') or self._ldap_props is None:
            config = self._config
            self._ldap_props = LDAPProps(
                uri=config.uri,
                user=config.user,
                password=config.password,
                cache=int(config.cache))
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
            node = LDAPNode(self._config.users_dn,
                            self.parent['ugm_server'].ldap_props)
            return len(node) >= 0
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
            expiresAttr = None
            expiresUnit = EXPIRATION_DAYS
            if config.users_account_expiration == 'True':
                expiresAttr = config.users_expires_attr
                expiresUnit = int(config.users_expires_unit)
                map[expiresAttr] = expiresAttr
            import cone.ugm.model
            self._ldap_ucfg = LDAPUsersConfig(
                baseDN=config.users_dn,
                attrmap=map,
                scope=int(config.users_scope),
                queryFilter=config.users_query,
                objectClasses=config.users_object_classes,
                defaults=cone.ugm.model.factory_defaults.user,
                expiresAttr=expiresAttr,
                expiresUnit=expiresUnit)
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
            node = LDAPNode(self._config.groups_dn,
                            self.parent['ugm_server'].ldap_props)
            return len(node) >= 0
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


class RolesSettings(UgmSettings):
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Roles Settings"
        metadata.description = "LDAP roles settings"
        return metadata
    
    @property
    def ldap_roles_container_valid(self):
        try:
            node = LDAPNode(self._config.roles_dn,
                            self.parent['ugm_server'].ldap_props)
            return len(node) >= 0
        except ldap.LDAPError:
            return False
    
    @property
    def ldap_rcfg(self):
        if not hasattr(self, '_ldap_rcfg') or self._ldap_rcfg is None:
            config = self._config
            map = dict()
            for key in config.roles_aliases_attrmap.keys():
                map[key] = config.roles_aliases_attrmap[key]
            for key in config.roles_form_attrmap.keys():
                if key in ['id']:
                    continue
                map[key] = key
            import cone.ugm.model
            self._ldap_rcfg = LDAPRolesConfig(
                baseDN=config.roles_dn,
                attrmap=map,
                scope=int(config.roles_scope),
                queryFilter=config.roles_query,
                objectClasses=config.roles_object_classes,
                #member_relation=config.roles_relation,
                defaults=cone.ugm.model.factory_defaults.role,
                )
        return self._ldap_rcfg