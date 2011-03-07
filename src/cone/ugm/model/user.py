from zope.interface import implements
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