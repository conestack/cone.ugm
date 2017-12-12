from plumber import plumber
from node.locking import locktree
from node.utils import instance_property
from pyramid.i18n import TranslationStringFactory
from cone.app.model import AdapterNode
from cone.app.model import Properties
from cone.app.model import Metadata
from cone.app.model import NodeInfo
from cone.app.model import registerNodeInfo
from cone.ugm.model.localmanager import LocalManagerGroupACL


_ = TranslationStringFactory('cone.ugm')


class Group(AdapterNode):
    __metaclass__ = plumber
    __plumbing__ = LocalManagerGroupACL

    node_info_name = 'group'

    @instance_property
    def properties(self):
        props = Properties()
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('group_node', 'Group')
        metadata.description = _('group_node_description', 'Group')
        return metadata

    @locktree
    def __call__(self):
        self.model()


info = NodeInfo()
info.title = _('group_node', 'Group')
info.description = _('group_node_description', 'Group')
info.node = Group
info.addables = []
registerNodeInfo('group', info)
