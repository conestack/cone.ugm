from yafowil.base import factory
from plumber import (
    Part,
    default,
    plumb,
)

class PrincipalRolesForm(Part):
    
    @default
    @property
    def roles_vocab(self):
        return [
            ('viewer', 'Viewer'),
            ('editor', 'Editor'),
            ('owner', 'Owner'),
            ('manager', 'Manager'),
        ]
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'principal_roles' as selection to 
        ``self.form``.
        """
        _next(self)
        value = []
        roles_widget = factory(
            'field:label:select',
            name='principal_roles',
            value=value,
            props={
                'label': 'User roles',
                'multivalued': True,
                'vocabulary': self.roles_vocab,
                'format': 'checkbox',
            },
        )
        save_widget = self.form['save']
        self.form.insertbefore(roles_widget, save_widget)
    
    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)