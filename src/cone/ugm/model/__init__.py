from pyramid.security import (
    Everyone,
    Allow,
    Deny,
    ALL_PERMISSIONS,
)
from cone.app.model import Properties

admin_permissions = ['view', 'add', 'edit', 'delete', 'manage_membership']

UGM_DEFAULT_ACL = [
    (Allow, 'role:editor', ['view', 'manage_membership']),
    (Allow, 'role:admin', admin_permissions),
    (Allow, 'role:owner', admin_permissions),
    (Allow, 'role:manager', admin_permissions + ['manage']),
    (Allow, Everyone, ['login']),
    (Deny, Everyone, ALL_PERMISSIONS),
]

# user and group factory defaults
factory_defaults = Properties()
factory_defaults.user = dict()
factory_defaults.group = dict()
factory_defaults.role = dict()