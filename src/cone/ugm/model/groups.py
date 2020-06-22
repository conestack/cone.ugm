from cone.app.model import AppNode
from cone.app.model import Metadata
from cone.app.model import node_info
from cone.app.model import Properties
from cone.app.ugm import ugm_backend
from cone.ugm.browser.utils import unquote_slash
from cone.ugm.localmanager import LocalManagerGroupsACL
from cone.ugm.model.group import Group
from node.behaviors import Nodify
from node.locking import locktree
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


@node_info(
    'groups',
    title=_('groups_node', default='Groups'),
    description=_(
        'groups_node_description',
        default='Container for Groups'),
    icon='ion-person-stalker',
    addables=['group'])
@plumbing(
    LocalManagerGroupsACL,
    AppNode,
    Nodify)
class Groups(object):

    @instance_property
    def properties(self):
        props = Properties()
        props.in_navtree = True
        return props

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _('groups_node', default='Groups')
        metadata.description = _(
            'groups_node_description',
            default='Container for Groups'
        )
        return metadata

    @property
    def backend(self):
        return ugm_backend.ugm.groups

    @locktree
    def invalidate(self, key=None):
        if key is None:
            self.backend.parent.invalidate('groups')
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
        return Group(model, name, self)
