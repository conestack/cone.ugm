from zope.interface import implements
from pyramid.security import (
    Everyone,
    Allow,
    Deny,
    ALL_PERMISSIONS,
)
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IUser


class User(AdapterNode):
    
    implements(IUser)
    
    node_info_name = 'user'
    
    __acl__ = [
        (Allow, 'group:authenticated', 'view'),
        (Allow, 'group:authenticated', 'edit'),
        (Allow, Everyone, 'login'),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]
    
    @property
    def properties(self):
        props = Properties()
        props.editable = True
        return props
    
    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "User"
        metadata.description = "User"
        return metadata
    
    def __call__(self):
        self.model()

info = BaseNodeInfo()
info.title = 'User'
info.description = 'User'
info.node = User
info.addables = []
registerNodeInfo('user', info)