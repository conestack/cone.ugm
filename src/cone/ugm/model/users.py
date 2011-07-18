from zope.interface import implements
from node.ext.ldap.ugm import Users as LDAPUsers
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IUsers
from cone.ugm.model.user import User
from cone.ugm.model.utils import (
    ugm_settings,
    ugm_backend,
)
from cone.ugm.browser.utils import unquote_slash


class Users(BaseNode):
    implements(IUsers)

    node_info_name = 'users'

    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Users"
        metadata.description = "Container for Users"
        return metadata
    
    @property
    def backend(self):
        return ugm_backend(self).users

    def invalidate(self):
        self.clear()
        del self.backend.parent.storage['users']

    def __iter__(self):
        try:
            for key in self.backend:
                yield key
        except Exception, e:
            # XXX: explicit exception, define in node.ext.ugm
            raise e

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
            user = User(self.backend[name], name, self)
            self[name] = user
            return user

info = BaseNodeInfo()
info.title = 'Users'
info.description = 'Users Container.'
info.node = Users
info.addables = ['user']
registerNodeInfo('users', info)
