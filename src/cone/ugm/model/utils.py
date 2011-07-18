import os
import cone.ugm
from node.ext.ldap.ugm import (
    UsersConfig,
    GroupsConfig,
    Ugm,
)

APP_PATH = os.environ['APP_PATH']

users_and_groups_mapped = 0

def map_users_and_groups(model):
    # XXX: currently the ldap users and groups need to know
    # mutually about themselves. Feels like node.ext.ugm should
    # present us the combo.
    from cone.ugm.model import utils
    if utils.users_and_groups_mapped:
        return
    model = model.root
    model['users'].ldap_users.groups = model['groups'].ldap_groups
    model['groups'].ldap_groups.users = model['users'].ldap_users
    utils.users_and_groups_mapped = 1


def ugm_settings(model):
    return model.root['settings']['ugm']


def ugm_backend(model, props=None, ucfg=None, gcfg=None, rcfg=None):
    # return backend if already initialized
    if cone.ugm.backend is not None:
        return cone.ugm.backend
    # if no kwargs given, read from settings. If kwargs given, we assume the
    # use from testing code
    if not props and not ucfg and not gfcg:
        settings = ugm_settings(model)
        props = settings.ldap_props
        ucfg = settings.ldap_ucfg
        gcfg = settings.ldap_gcfg    
        rcfg = settings.ldap_rcfg
    cone.ugm.backend = Ugm(name='ugm', parent=None, props=props,
                           ucfg=ucfg, gcfg=gcfg, rcfg=rcfg)
    return cone.ugm.backend