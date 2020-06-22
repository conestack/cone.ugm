from cone.app.model import AdapterNode
from cone.app.model import Metadata
from cone.app.model import node_info
from cone.app.model import Properties
from cone.ugm.localmanager import LocalManagerGroupACL
from node.locking import locktree
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('cone.ugm')


@node_info(
    'group',
    title=_('group_node', default='Group'),
    description=_('group_node_description', default='Group'))
@plumbing(LocalManagerGroupACL)
class Group(AdapterNode):

    @instance_property
    def properties(self):
        props = Properties()
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('group_node', default='Group')
        metadata.description = _('group_node_description', default='Group')
        return metadata

    @locktree
    def __call__(self):
        self.model()
