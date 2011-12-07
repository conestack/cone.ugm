from node.locking import locktree
from node.utils import instance_property
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)


class User(AdapterNode):
    node_info_name = 'user'
    
    @instance_property
    def properties(self):
        props = Properties()
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