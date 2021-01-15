
class UserManagementEvent(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password


class UserCreatedEvent(UserManagementEvent):
    "called after a user has been created"


class UserModifiedEvent(UserManagementEvent):
    "called after a user has been deleted"


class UserDeletedEvent(UserManagementEvent):
    def __init__(self, user):
        self.user = user

