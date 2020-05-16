from cone.app.model import BaseNode
from cone.app.model import Metadata
from cone.app.model import node_info
from cone.app.model import Properties
from cone.app.ugm import ugm_backend
from cone.ugm.browser.utils import unquote_slash
from cone.ugm.layout import UGMLayout
from cone.ugm.localmanager import LocalManagerGroupsACL
from cone.ugm.model.group import Group
from node.locking import locktree
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
import logging


logger = logging.getLogger('cone.ugm')
_ = TranslationStringFactory('cone.ugm')


def groups_factory():
    return Groups()


@node_info(
    'groups',
    title=_('groups_node', default='Groups'),
    description=_(
        'groups_node_description',
        default='Container for Groups'),
    icon='ion-person-stalker',
    addables=['group'])
@plumbing(LocalManagerGroupsACL)
class Groups(BaseNode):

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

    @instance_property
    def layout(self):
        return UGMLayout(model=self)

    @property
    def backend(self):
        return ugm_backend.ugm.groups

    @locktree
    def invalidate(self, key=None):
        if key is None:
            self.backend.parent.invalidate('groups')
            self.clear()
            return
        self.backend.invalidate(key)
        try:
            del self[key]
        except KeyError:
            pass

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
            return BaseNode.__getitem__(self, name)
        except KeyError:
            try:
                model = self.backend[name]
            except AttributeError:
                raise KeyError(name)
            group = Group(model, name, self)
            self[name] = group
            return group
