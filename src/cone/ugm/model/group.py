from zope.interface import implements
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IGroup


class Group(AdapterNode):
    
    implements(IGroup)
    
    node_info_name = 'group'
    
    @property
    def properties(self):
        props = Properties()
        props.editable = True
        return props
    
    @property
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