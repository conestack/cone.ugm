
class PrincipalmanagementEvent(object):
    def __init__(self, principal=None, uid=None):
        self.principal = principal
        self.uid = uid


class UserCreatedEvent(PrincipalmanagementEvent):
    "called after a user has been created"
    def __init__(self, principal=None, uid=None, password=None):
        self.principal = principal
        self.uid = uid
        self.password = password


class UserModifiedEvent(PrincipalmanagementEvent):
    "called after a user has been deleted"
    def __init__(self, principal=None, uid=None, password=None):
        self.principal = principal
        self.uid = uid
        self.password = password


class UserDeletedEvent(PrincipalmanagementEvent):
    """called on user deletion"""


class GroupCreatedEvent(PrincipalmanagementEvent):
    """called on group creation"""


class GroupModifiedEvent(PrincipalmanagementEvent):
    """called on group modification"""


class GroupDeletedEvent(PrincipalmanagementEvent):
    """called on group deletiion"""
