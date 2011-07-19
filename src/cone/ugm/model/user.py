from zope.interface import implements
from node.utils import instance_property
from cone.app.model import (
    AdapterNode,
    ProtectedProperties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.app.security import DEFAULT_NODE_PROPERTY_PERMISSIONS
from cone.ugm.model.interfaces import IUser


class User(AdapterNode):
    
    implements(IUser)
    
    node_info_name = 'user'
    
    @instance_property
    def properties(self):
        props = ProtectedProperties(self, DEFAULT_NODE_PROPERTY_PERMISSIONS)
        props.editable = True
        return props
    
    @instance_property
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