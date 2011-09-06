import logging
from node.locking import locktree
from node.utils import instance_property
from node.ext.ldap.ugm import Users as LDAPUsers
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model import UGM_DEFAULT_ACL
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_backend
from cone.ugm.browser.utils import unquote_slash


logger = logging.getLogger('cone.ugm')


class Users(BaseNode):
    
    __acl__ = UGM_DEFAULT_ACL

    node_info_name = 'users'

    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Users"
        metadata.description = "Container for Users"
        return metadata
    
    @property
    def backend(self):
        return ugm_backend(self).users

    @locktree
    def invalidate(self):
        self.clear()
        del self.backend.parent.storage['users']

    @locktree
    def __call__(self):
        self.backend()
    
    @locktree
    def __iter__(self):
        try:
            return self.backend.__iter__()
        except Exception, e:
            logger.error(str(e))
            return iter(list())

    iterkeys = __iter__

    @locktree
    def __getitem__(self, name):
        # XXX: temporary hack until paster/webob/pyramid handle urllib
        # quoted slashes in path components
        name = unquote_slash(name)
        try:
            return BaseNode.__getitem__(self, name)
        except KeyError:
            model = self.backend[name]
            user = User(model, name, self)
            self[name] = user
            return user

info = BaseNodeInfo()
info.title = 'Users'
info.description = 'Users Container.'
info.node = Users
info.addables = ['user']
registerNodeInfo('users', info)
