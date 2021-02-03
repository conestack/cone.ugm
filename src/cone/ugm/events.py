class PrincipalManagementEvent(object):
    """Principal management related base event.
    """

    def __init__(self, principal):
        self.principal = principal


class UserCreatedEvent(PrincipalManagementEvent):
    """Called after a user has been created.
    """

    def __init__(self, principal, password=None):
        self.principal = principal
        self.password = password


class UserModifiedEvent(PrincipalManagementEvent):
    """Called after a user has been modified.
    """

    def __init__(self, principal, password=None):
        self.principal = principal
        self.password = password


class UserDeletedEvent(PrincipalManagementEvent):
    """Called after a user has been deleted.
    """


class GroupCreatedEvent(PrincipalManagementEvent):
    """Called after a group has been created.
    """


class GroupModifiedEvent(PrincipalManagementEvent):
    """Called after a group has been modified.
    """


class GroupDeletedEvent(PrincipalManagementEvent):
    """Called after a group has been deleted.
    """
