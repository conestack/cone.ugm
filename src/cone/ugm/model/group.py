from zope.interface import implements
from pyramid.security import (
    Everyone,
    Allow,
    Deny,
    ALL_PERMISSIONS,
)
from cone.app.model import (
    AdapterNode,
    Properties,
    BaseMetadata,
)
from cone.ugm.model.interfaces import IGroup

class Group(AdapterNode):
    
    implements(IGroup)
    
    __acl__ = [
        (Allow, 'group:authenticated', 'view'),
        (Allow, 'group:authenticated', 'edit'),
        (Allow, Everyone, 'login'),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]
    
    @property
    def properties(self):
        props = Properties()
        props.editable = True
        return props
    
    @property
    def metadata(self):
        metadata = BaseMetadata()
        metadata.title = "Group"
        metadata.description = "Group"
        return metadata
    
    def __call__(self):
        self.model()