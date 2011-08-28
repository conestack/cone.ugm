from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.security import has_permission
from yafowil.base import factory
from cone.ugm.model.utils import ugm_roles


class PrincipalRolesForm(Part):
    
    @default
    @property
    def roles_vocab(self):
        from cone.app.security import DEFAULT_ROLES
        return DEFAULT_ROLES
    
    @default
    @property
    def roles_support(self):
        return ugm_roles(self.model).ldap_roles_container_valid
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'principal_roles' as selection to 
        ``self.form``.
        """
        _next(self)
        if not self.roles_support:
            return
        if not has_permission('manage', self.model.parent, self.request):
            # XXX: yafowil selection display renderer
            return
        value = []
        if self.action_resource == 'edit':
            value = self.model.model.roles
        roles_widget = factory(
            'field:label:select',
            name='principal_roles',
            value=value,
            props={
                'label': 'Roles',
                'multivalued': True,
                'vocabulary': self.roles_vocab,
                'format': 'single',
                'listing_tag': 'ul',
                'listing_label_position': 'after',
            },
        )
        save_widget = self.form['save']
        self.form.insertbefore(roles_widget, save_widget)
    
    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)
        if not self.roles_support:
            return
        if not has_permission('manage', self.model.parent, self.request):
            return
        existing_roles = list()
        if self.action_resource == 'edit':
            principal = self.model.model
            existing_roles = principal.roles
        else:
            id = data.fetch('%s.id' % self.form_name).extracted
            principal = self.model.parent[id].model
        new_roles = data.fetch('%s.principal_roles' % self.form_name).extracted
        removed_roles = list()
        for role in existing_roles:
            if not role in new_roles:
                principal.remove_role(role)
                removed_roles.append(role)
        for role in removed_roles:
            existing_roles.remove(role)
        for role in new_roles:
            if not role in existing_roles:
                principal.add_role(role)
        principal.parent.parent()