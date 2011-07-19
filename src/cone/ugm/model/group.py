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
from cone.ugm.model.interfaces import IGroup


class Group(AdapterNode):
    
    implements(IGroup)
    
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
    
    def __call__(self):
        self.model()

info = BaseNodeInfo()
info.title = 'Group'
info.description = 'Group'
info.node = Group
info.addables = []
registerNodeInfo('group', info)