import os
from node.ext.ldap.ugm import (
    UsersConfig,
    GroupsConfig,
    Ugm,
)
import cone.ugm

APP_PATH = os.environ['APP_PATH']

users_and_groups_mapped = 0

#def map_users_and_groups(model):
#    # XXX: currently the ldap users and groups need to know
#    # mutually about themselves. Feels like node.ext.ugm should
#    # present us the combo.
#    from cone.ugm.model import utils
#    if utils.users_and_groups_mapped:
#        return
#    model = model.root
#    model['users'].ldap_users.groups = model['groups'].ldap_groups
#    model['groups'].ldap_groups.users = model['users'].ldap_users
#    utils.users_and_groups_mapped = 1


def ugm_settings(model):
    if isinstance(model, cone.ugm.model.settings.UgmSettings):
        return model
    return model.root['settings']['ugm']


def ugm_backend(model):
    # return backend if already initialized
    import cone.ugm
    if cone.ugm.backend is not None:
        return cone.ugm.backend
    settings = ugm_settings(model)
    props = settings.ldap_props
    ucfg = settings.ldap_ucfg
    gcfg = settings.ldap_gcfg    
    rcfg = settings.ldap_rcfg
    cone.ugm.backend = Ugm(name='ugm', parent=None, props=props,
                           ucfg=ucfg, gcfg=gcfg, rcfg=rcfg)
    return cone.ugm.backend