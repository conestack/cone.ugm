from zope.interface import implements
from node.ext.ldap.ugm import Groups as LDAPGroups
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IGroups
from cone.ugm.model.group import Group


class Groups(BaseNode):

    implements(IGroups)

    node_info_name = 'groups'

    def __init__(self, props=None, gcfg=None):
        """``props`` and `gcfg`` just needed for testing. never used in
        application code.
        """
        super(Groups, self).__init__()
        self._testenv = None
        if props or gcfg:
            self._testenv = {
                'props': props,
                'gcfg': gcfg,
            }
        self._ldap_groups = None

    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups"
        metadata.description = "Container for Groups"
        return metadata

    @property
    def settings(self):
        return self.__parent__['settings']

    @property
    def ldap_groups(self):
        if self._ldap_groups is None:
            if self._testenv is not None:
                props = self._testenv['props']
                gcfg = self._testenv['gcfg']
            else:
                settings = self.settings
                props = settings.ldap_props
                gcfg = settings.ldap_gcfg
            self._ldap_groups = LDAPGroups(props, gcfg)
        return self._ldap_groups

    def invalidate(self):
        """
        - get rid of ldap_groups
        - get new ldap_groups
        - tell it about ldap_users
        - tell ldap_users about new ldap_groups
        """
        self._ldap_groups = None
        self.clear()
        self.ldap_groups.users = self.__parent__['users'].ldap_users
        self.__parent__['users'].ldap_users.groups = self.ldap_groups

    def __iter__(self):
        try:
            for key in self.ldap_groups:
                yield key
        except Exception, e:
            # XXX: explicit exception
            print e

    iterkeys = __iter__

    def __getitem__(self, name):
        try:
            return BaseNode.__getitem__(self, name)
        except KeyError:
            if not name in self.iterkeys():
                raise KeyError(name)
            group = Group(self.ldap_groups[name], name, self)
            self[name] = group
            return group

info = BaseNodeInfo()
info.title = 'Groups'
info.description = 'Groups Container.'
info.node = Groups
info.addables = ['group']
registerNodeInfo('groups', info)
