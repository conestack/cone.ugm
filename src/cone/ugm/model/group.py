from node.locking import locktree
from node.utils import instance_property
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)


class Group(AdapterNode):
    node_info_name = 'group'
    
    @instance_property
    def properties(self):
        props = Properties()
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