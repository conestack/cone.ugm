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


class Group(AdapterNode):
    
    __acl__ = UGM_DEFAULT_ACL
    
    node_info_name = 'group'
    
    @instance_property
    def properties(self):
        props = ProtectedProperties(self, DEFAULT_NODE_PROPERTY_PERMISSIONS)
        props.editable = True
        return props
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Group"
        metadata.description = "Group"
        return metadata
    
    @locktree
    def __call__(self):
        self.model()

info = BaseNodeInfo()
info.title = 'Group'
info.description = 'Group'
info.node = Group
info.addables = []
registerNodeInfo('group', info)