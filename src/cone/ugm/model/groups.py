from zope.interface import implements
from cone.app.model import (
    BaseNode,
    Properties,
    BaseMetadata,
)
from cone.ugm.model.interfaces import IGroups
from cone.ugm.model.group import Group


class Groups(BaseNode):
    
    implements(IGroups)
    
    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Groups"
        metadata.description = "Container for Groups"
        return metadata
    
    def __iter__(self):
        for i in range(1000):
            yield 'group%i' % i
    
    iterkeys = __iter__
    
    def __getitem__(self, name):
        try:
            return BaseNode.__getitem__(self, name)
        except KeyError:
            if not name in self.iterkeys():
                raise KeyError(name)
            # XXX: Group(ldapNode, name, self)
            group = Group(BaseNode(), name, self)
            self[name] = group
            return group