from cone.app.model import Properties
from .users import Users
from .user import User
from .groups import Groups
from .group import Group


# user and group factory defaults
factory_defaults = Properties()
factory_defaults.user = dict()
factory_defaults.group = dict()
factory_defaults.role = dict()
