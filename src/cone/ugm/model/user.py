from cone.app.model import AdapterNode
from cone.app.model import Metadata
from cone.app.model import node_info
from cone.app.model import Properties
from cone.ugm.localmanager import LocalManagerUserACL
from node.locking import locktree
from node.utils import instance_property
from plumber import Behavior
from plumber import plumb
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from pyramid.security import Allow
from pyramid.threadlocal import get_current_request


_ = TranslationStringFactory('cone.ugm')


class OwnUserACL(Behavior):
    """Behavior providing ACL for own user permissions.
    """

    @plumb
    @property
    def __acl__(_next, self):
        acl = _next(self)
        request = get_current_request()
        if request.authenticated_userid == self.name:
            acl = [(Allow, self.name, ['change_own_password'])] + acl
        return acl


@node_info(
    'user',
    title=_('user_node', default='User'),
    description=_('user_node_description', default='User'))
@plumbing(
    OwnUserACL,
    LocalManagerUserACL)
class User(AdapterNode):

    @instance_property
    def properties(self):
        props = Properties()
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('user_node', default='User')
        metadata.description = _('user_node_description', default='User')
        return metadata

    @locktree
    def __call__(self):
        self.model()
