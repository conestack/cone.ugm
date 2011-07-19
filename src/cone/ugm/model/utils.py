import os
from node.ext.ldap.ugm import (
    UsersConfig,
    GroupsConfig,
    Ugm,
)
import cone.ugm

APP_PATH = os.environ['APP_PATH']

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