import os
import types
from lxml import etree
from plumber import (
    Part,
    plumber,
    plumb,
    default,
    finalize,
)
from node.parts import (
    Nodify,
    DictStorage,
)
from pyramid.security import Allow
from pyramid.threadlocal import get_current_request
from cone.app.security import authenticated_user


class LocalManagerConfig(DictStorage):
    """Local Management configuration storage.
    """
    
    @finalize
    def load(self):
        path = self.file_path
        if not path or not os.path.exists(path):
            return
        with open(path, 'r') as handle:
            tree = etree.parse(handle)
        root = tree.getroot()
        for rule in root.getchildren():
            new_rule = self.storage[rule.tag] = dict()
            for prop in rule.getchildren():
                for tag_name in ['target', 'default']:
                    if prop.tag == tag_name:
                        new_rule[tag_name] = list()
                        for group in prop.getchildren():
                            new_rule[tag_name].append(group.text)
    
    @finalize
    def __call__(self):
        root = etree.Element('localmanager')
        for gid, rule in self.storage.items():
            group = etree.SubElement(root, gid)
            for tag_name in ['target', 'default']:
                elem = etree.SubElement(group, tag_name)
                for gid in rule[tag_name]:
                    item = etree.SubElement(elem, 'item')
                    item.text = gid
        with open(self.file_path, 'w') as handle:
            handle.write(etree.tostring(root, pretty_print=True))


class LocalManagerConfigAttributes(object):
    __metaclass__ = plumber
    __plumbing__ = (
        Nodify,
        LocalManagerConfig,
    )
    
    def __init__(self, path):
        self.file_path = path
        self.load()


class LocalManager(Part):
    """Part providing local manager information for authenticated user.
    """
    
    @finalize
    @property
    def local_management_enabled(self):
        general_settings = self.root['settings']['ugm_general']
        return general_settings.attrs.users_local_management_enabled == 'True'
    
    @finalize
    @property
    def local_manager_target_gids(self):
        config = self.root['settings']['ugm_localmanager'].attrs
        user = authenticated_user(get_current_request())
        gids = user.group_ids
        managed_gids = set()
        for gid in gids:
            for rule in config.get(gid, []):
                managed_gids.update(rule['target'])
        return list(managed_gids)
    
    @finalize
    @property
    def local_manager_target_uids(self):
        groups = self.root['groups'].backend
        managed_uids = set()
        for gid in self.local_manager_target_gids:
            group = groups.get(gid)
            if group:
                managed_uids.update(group.member_ids)
        return list(managed_uids)
    
    @finalize
    def local_manager_is_default(self, gid):
        config = self.root['settings']['ugm_localmanager'].attrs
        for rule in config.values():
            if gid in rule['default']:
                return True
        return False


class LocalManagerACL(LocalManager):
    """Part providing ACL's by local manager configuration.
    """

    @default
    @property
    def local_manager_acl(self):
        raise NotImplementedError(u"Abstract ``LocalManagerACL`` does not "
                                  u"implement ``local_manager_acl``")
    
    @plumb
    @property
    def __acl__(_next, self):
        acl = _next(self)
        if not self.local_management_enabled:
            return acl
        roles = authenticated_user(self.request).roles
        if 'admin' in roles or 'manager' in roles:
            return acl
        return self.local_manager_acl + _next(self)


class LocalManagerUsersACL(LocalManagerACL):
    
    @finalize
    @property
    def local_manager_acl(self):
        """Permit ``view``, ``add_user`` and for local manager.
        """
        return []


class LocalManagerUserACL(LocalManagerACL):
    
    @finalize
    @property
    def local_manager_acl(self):
        """Permit ``view``, ``edit_user``, ``manage_expiration`` for local
        manager.
        """
        return []


class LocalManagerGroupsACL(LocalManagerACL):
    
    @finalize
    @property
    def local_manager_acl(self):
        """Permit ``view`` for local manager.
        """
        return []


class LocalManagerGroupACL(LocalManagerACL):
    
    @finalize
    @property
    def local_manager_acl(self):
        """Permit ``view`` and ``manage_membership`` for local manager.
        """
        return []
