import os

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