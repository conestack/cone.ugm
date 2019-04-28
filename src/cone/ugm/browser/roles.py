from plumber import Behavior
from plumber import default
from plumber import plumb
from pyramid.i18n import TranslationStringFactory
from yafowil.base import factory


_ = TranslationStringFactory('cone.ugm')


class PrincipalRolesForm(Behavior):

    @default
    @property
    def roles_vocab(self):
        from cone.app.security import DEFAULT_ROLES
        return DEFAULT_ROLES

    @default
    @property
    def roles_support(self):
        # XXX: LDAP
        settings = self.model.root['settings']['ldap_roles']
        return settings.container_exists

    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'principal_roles' as selection to
        ``self.form``.
        """
        _next(self)
        if not self.roles_support:
            return
        if not self.request.has_permission('manage', self.model.parent):
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
                'label': _('roles', default='Roles'),
                'multivalued': True,
                'vocabulary': self.roles_vocab,
                'format': 'single',
                'listing_tag': 'ul',
                'listing_label_position': 'after',
            })
        save_widget = self.form['save']
        self.form.insertbefore(roles_widget, save_widget)

    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)
        if not self.roles_support:
            return
        if not self.request.has_permission('manage', self.model.parent):
            return
        existing_roles = list()
        if self.action_resource == 'edit':
            principal = self.model.model
            existing_roles = principal.roles
        else:
            uid = data.fetch('%s.id' % self.form_name).extracted
            principal = self.model.parent[uid].model
        new_roles = data.fetch('%s.principal_roles' % self.form_name).extracted
        removed_roles = list()
        for role in existing_roles:
            if role not in new_roles:
                principal.remove_role(role)
                removed_roles.append(role)
        for role in removed_roles:
            existing_roles.remove(role)
        for role in new_roles:
            if role not in existing_roles:
                principal.add_role(role)
        principal.parent.parent()
