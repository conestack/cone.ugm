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
from cone.ugm.model.utils import (
    ugm_settings,
    ugm_backend,
)
from cone.ugm.browser.utils import unquote_slash


class Groups(BaseNode):

    implements(IGroups)

    node_info_name = 'groups'

    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups"
        metadata.description = "Container for Groups"
        return metadata

    @property
    def model(self):
        if hasattr(self, '_model'):
            return self._model.groups
        if hasattr(self, '_testenv'):
            props = self._testenv['props']
            ucfg = self._testenv['ucfg']
            gcfg = self._testenv['gcfg']
            rcfg = None
            self._model = ugm_backend(self, props, ucfg, gcfg, rcfg)
        else:
            self._model = ugm_backend(self)
        return self._model.groups

    def invalidate(self):
        """
        - get rid of ldap_groups
        - get new ldap_groups
        - tell it about ldap_users
        - tell ldap_users about new ldap_groups
        """
        self._model = None
        self.clear()
        #self.ldap_groups.users = self.__parent__['users'].ldap_users
        #self.__parent__['users'].ldap_users.groups = self.ldap_groups

    def __iter__(self):
        try:
            for key in self.model:
                yield key
        except Exception, e:
            # XXX: explicit exception
            print e

    iterkeys = __iter__

    def __getitem__(self, name):
        # XXX: temporary hack until paster/webob/pyramid handle urllib
        # quoted slashes in path components
        name = unquote_slash(name)
        try:
            return BaseNode.__getitem__(self, name)
        except KeyError:
            if not name in self.iterkeys():
                raise KeyError(name)
            group = Group(self.model[name], name, self)
            self[name] = group
            return group

info = BaseNodeInfo()
info.title = 'Groups'
info.description = 'Groups Container.'
info.node = Groups
info.addables = ['group']
registerNodeInfo('groups', info)
