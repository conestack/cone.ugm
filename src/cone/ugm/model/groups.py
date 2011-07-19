from zope.interface import implements
from node.utils import instance_property
from node.ext.ldap.ugm import Groups as LDAPGroups
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
    BaseNodeInfo,
    registerNodeInfo,
)
from cone.ugm.model.interfaces import IGroups
from cone.ugm.model.group import Group
from cone.ugm.model.utils import (
    ugm_settings,
    ugm_backend,
)
from cone.ugm.browser.utils import unquote_slash


class Groups(BaseNode):

    implements(IGroups)

    node_info_name = 'groups'

    @instance_property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups"
        metadata.description = "Container for Groups"
        return metadata

    @property
    def backend(self):
        return ugm_backend(self).groups

    def invalidate(self):
        self.clear()
        del self.backend.parent.storage['groups']

    def __iter__(self):
        try:
            for key in self.backend:
                yield key
        except Exception, e:
            # XXX: explicit exception, define in node.ext.ugm
            raise e

    iterkeys = __iter__

    def __getitem__(self, name):
        # XXX: temporary hack until paster/webob/pyramid handle urllib
        # quoted slashes in path components
        name = unquote_slash(name)
        try:
            return BaseNode.__getitem__(self, name)
        except KeyError:
            if not name in self.iterkeys():
                raise KeyError(name)
            group = Group(self.backend[name], name, self)
            self[name] = group
            return group

info = BaseNodeInfo()
info.title = 'Groups'
info.description = 'Groups Container.'
info.node = Groups
info.addables = ['group']
registerNodeInfo('groups', info)
