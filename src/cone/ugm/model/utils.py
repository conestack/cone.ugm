import os
from node.ext.ldap.ugm import (
    UsersConfig,
    GroupsConfig,
    Ugm,
)
import cone.ugm


def ldap_cfg_file():
    return os.environ['LDAP_CFG_FILE']


def ugm_general(model):
    return model.root['settings']['ugm_general']


def ugm_server(model):
    return model.root['settings']['ugm_server']


def ugm_users(model):
    return model.root['settings']['ugm_users']


def ugm_groups(model):
    return model.root['settings']['ugm_groups']


def ugm_roles(model):
    return model.root['settings']['ugm_roles']


def ugm_backend(model):
    """Always access UGM backend via this function. Currently
    ``cone.app.cfg.auth`` is returned. This might change in future if multiple
    backend management get supported.
    """
    import cone.app
    # return backend if already initialized
    if cone.app.cfg.auth is not None:
        return cone.app.cfg.auth
    import cone.ugm
    return cone.ugm.reset_auth_impl()