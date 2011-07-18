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
    def model(self):
        if hasattr(self, '_model'):
            return self._model.users
        if hasattr(self, '_testenv'):
            props = self._testenv['props']
            ucfg = self._testenv['ucfg']
            gcfg = self._testenv['gcfg']
            rcfg = None
            self._model = ugm_backend(self, props, ucfg, gcfg, rcfg)
        else:
            self._model = ugm_backend(self)
        return self._model.users

    def invalidate(self):
        del self.model.parent.storage['users']
        self.clear()

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
            user = User(self.model[name], name, self)
            self[name] = user
            return user

info = BaseNodeInfo()
info.title = 'Users'
info.description = 'Users Container.'
info.node = Users
info.addables = ['user']
registerNodeInfo('users', info)
