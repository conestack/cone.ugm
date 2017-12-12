from cone.app.model import AdapterNode
from cone.app.model import Metadata
from cone.app.model import NodeInfo
from cone.app.model import Properties
from cone.app.model import node_info
from cone.ugm.model.localmanager import LocalManagerUserACL
from node.locking import locktree
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('cone.ugm')


@node_info(
    'user',
    title=_('user_node', 'User'),
    description=_('user_node_description', 'User'))
@plumbing(LocalManagerUserACL)
class User(AdapterNode):

    @instance_property
    def properties(self):
        props = Properties()
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('user_node', 'User')
        metadata.description = _('user_node_description', 'User')
        return metadata

    @locktree
    def __call__(self):
        self.model()
