from cone.app.model import Properties
from cone.ugm.model.users import Users
from cone.ugm.model.user import User
from cone.ugm.model.groups import Groups
from cone.ugm.model.group import Group


# user and group factory defaults
factory_defaults = Properties()
factory_defaults.user = dict()
factory_defaults.group = dict()
factory_defaults.role = dict()