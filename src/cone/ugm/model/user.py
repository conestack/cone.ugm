from node.locking import locktree
from node.utils import instance_property
from pyramid.i18n import TranslationStringFactory
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)

_ = TranslationStringFactory('cone.ugm')


class User(AdapterNode):
    node_info_name = 'user'
    
    @instance_property
    def properties(self):
        props = Properties()
        return props
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = _('user_node', 'User')
        metadata.description = _('user_node_description', 'User')
        return metadata
    
    @locktree
    def __call__(self):
        self.model()


info = BaseNodeInfo()
info.title = _('user_node', 'User')
info.description = _('user_node_description', 'User')
info.node = User
info.addables = []
registerNodeInfo('user', info)