import os


def ldap_cfg_file():
    return os.environ['LDAP_CFG_FILE']


def localmanager_cfg_file():
    return os.environ['LOCAL_MANAGER_CFG_FILE']


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
