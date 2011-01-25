from cone.ugm.model.ugm import Ugm
from cone.ugm.model.users import Users
from cone.ugm.model.user import User

root = Ugm()

def get_root(environ):
    return root