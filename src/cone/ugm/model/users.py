from cone.app.model import AppNode
from cone.app.model import Metadata
from cone.app.model import node_info
from cone.app.model import Properties
from cone.app.ugm import ugm_backend
from cone.ugm.browser.utils import unquote_slash
from cone.ugm.localmanager import LocalManagerUsersACL
from cone.ugm.model.user import User
from node.behaviors import Nodify
from node.locking import locktree
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@node_info(
    'users',
    title=_('users_node', default='Users'),
    description=_(
        'users_node_description',
        default='Container for Users'),
    icon='ion-person',
    addables=['user'])
@plumbing(
    LocalManagerUsersACL,
    AppNode,
    Nodify)
class Users(object):

    @instance_property
    def properties(self):
        props = Properties()
        props.in_navtree = True
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('users_node', default='Users')
        metadata.description = _(
            'users_node_description',
            default='Container for Users'
        )
        return metadata

    @property
    def backend(self):
        return ugm_backend.ugm.users

    @locktree
    def invalidate(self, key=None):
        if key is None:
            self.backend.parent.invalidate('users')
            return
        self.backend.invalidate(key)

    @locktree
    def __call__(self):
        self.backend()

    @locktree
    def __iter__(self):
        try:
            return self.backend.__iter__()
        except Exception as e:
            logger.error(str(e))
            return iter(list())

    iterkeys = __iter__

    @locktree
    def __getitem__(self, name):
        # XXX: temporary hack until paster/webob/pyramid handle urllib
        # quoted slashes in path components
        name = unquote_slash(name)
        try:
            model = self.backend[name]
        except AttributeError:
            raise KeyError(name)
        return User(model, name, self)
