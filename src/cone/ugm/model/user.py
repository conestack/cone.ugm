from node.locking import locktree
from node.utils import instance_property
from cone.app.model import (
    AdapterNode,
    ProtectedProperties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.app.security import DEFAULT_NODE_PROPERTY_PERMISSIONS
from cone.ugm.model import UGM_DEFAULT_ACL


class User(AdapterNode):
    
    __acl__ = UGM_DEFAULT_ACL
    
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
    
    @locktree
    def __call__(self):
        self.model()

info = BaseNodeInfo()
info.title = 'User'
info.description = 'User'
info.node = User
info.addables = []
registerNodeInfo('user', info)