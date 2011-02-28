from zope.interface import implements
from node.ext.ldap.users import LDAPUsers
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IUsers
from cone.ugm.model.user import User


class Users(BaseNode):
    
    implements(IUsers)
    
    node_info_name = 'users'
    
    def __init__(self, props=None, ucfg=None):
        """``props`` and `ucfg`` just needed for testing. never used in
        application code.
        """
        super(Users, self).__init__()
        self._testenv = None
        if props or ucfg:
            self._testenv = {
                'props': props,
                'ucfg': ucfg,
            }
        self._ldap_users = None

    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Users"
        metadata.description = "Container for Users"
        return metadata
    
    @property
    def settings(self):
        return self.__parent__['settings']
    
    @property
    def ldap_users(self):
        if self._ldap_users is None:
            if self._testenv is not None:
                props = self._testenv['props']
                ucfg = self._testenv['ucfg']
            else:
                settings = self.settings
                props = settings.ldap_props
                ucfg = settings.ldap_ucfg
            self._ldap_users = LDAPUsers(props, ucfg)
        return self._ldap_users

    def invalidate(self):
        self._ldap_users = None
        self.clear()

    def __iter__(self):
        try:
            for key in self.ldap_users:
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
            user = User(self.ldap_users[name], name, self)
            self[name] = user
            return user

info = BaseNodeInfo()
info.title = 'Users'
info.description = 'Users Container.'
info.node = Users
info.addables = ['user']
registerNodeInfo('users', info)