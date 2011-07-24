import os
from node.ext.ldap.ugm import (
    UsersConfig,
    GroupsConfig,
    Ugm,
)
import cone.ugm

APP_PATH = os.environ['APP_PATH']


def ugm_server(model):
    return model.root['settings']['ugm_server']


def ugm_users(model):
    return model.root['settings']['ugm_users']


def ugm_groups(model):
    return model.root['settings']['ugm_groups']


def ugm_backend(model):
    import cone.ugm
    if cone.ugm.backend is not None:
        # return backend if already initialized
        return cone.ugm.backend
    props = ugm_server(model).ldap_props
    ucfg = ugm_users(model).ldap_ucfg
    gcfg = ugm_groups(model).ldap_gcfg
    # XXX: later
    rcfg = None
    cone.ugm.backend = Ugm(name='ugm', parent=None, props=props,
                           ucfg=ucfg, gcfg=gcfg, rcfg=rcfg)
    return cone.ugm.backend