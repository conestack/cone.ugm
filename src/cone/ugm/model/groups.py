import logging
from node.locking import locktree
from node.utils import instance_property
from cone.app.model import (
    BaseNode,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
    Properties,
)
from cone.ugm.model.group import Group
from cone.ugm.model.utils import ugm_backend
from cone.ugm.browser.utils import unquote_slash


logger = logging.getLogger('cone.ugm')


def groups_factory():
    return Groups()


class Groups(BaseNode):
    node_info_name = 'groups'

    @instance_property
    def properties(self):
        props = Properties()
        props.in_navtree = True
        return props
    
    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups"
        metadata.description = "Container for Groups"
        return metadata

    @property
    def backend(self):
        return ugm_backend(self).groups

    @locktree
    def invalidate(self, key=None):
        if key is None:
            del self.backend.parent.storage['groups']
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
        except Exception, e:
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


info = BaseNodeInfo()
info.title = 'Groups'
info.description = 'Groups Container.'
info.node = Groups
info.addables = ['group']
info.icon = 'cone.ugm.static/images/groups16_16.png'
registerNodeInfo('groups', info)