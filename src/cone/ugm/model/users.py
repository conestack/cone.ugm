import logging
from plumber import plumber
from node.locking import locktree
from node.utils import instance_property
from pyramid.i18n import TranslationStringFactory
from cone.app.model import (
    BaseNode,
    Metadata,
    NodeInfo,
    registerNodeInfo,
    Properties,
)
from cone.ugm.model.localmanager import LocalManagerACL
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_backend
from cone.ugm.browser.utils import unquote_slash

logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


def users_factory():
    return Users()


class Users(BaseNode):
    __metaclass__ = plumber
    __plumbing__ = LocalManagerACL
    
    node_info_name = 'users'

    @instance_property
    def properties(self):
        props = Properties()
        props.in_navtree = True
        return props
    
    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('users_node', 'Users')
        metadata.description = _('users_node_description',
                                 'Container for Users')
        return metadata
    
    @property
    def backend(self):
        return ugm_backend(self).users
    
    @locktree
    def invalidate(self, key=None):
        if key is None:
            del self.backend.parent.storage['users']
            self.clear()
            return
        self.backend.invalidate(key)
        try:
            del self[key]
        except KeyError:
            pass
    
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
            try:
                model = self.backend[name]
            except AttributeError:
                raise KeyError(name)
            user = User(model, name, self)
            self[name] = user
            return user


info = NodeInfo()
info.title = _('users_node', 'Users')
info.description = _('users_node_description',
                     'Container for Users')
info.node = Users
info.addables = ['user']
info.icon = 'cone.ugm.static/images/users16_16.png'
registerNodeInfo('users', info)