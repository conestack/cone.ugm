from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.security import has_permission
from yafowil.base import factory
from cone.ugm.model.utils import ugm_users


def expiration_extractor(widget, data):
    pass


def expiration_edit_renderer(widget, data):
    pass


def expiration_display_renderer(widget, data):
    pass


factory.register(
    'expiration',
    extractors=[expiration_extractor], 
    edit_renderers=[expiration_edit_renderer],
    display_renderers=[expiration_display_renderer])


class ExpirationForm(Part):
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set expiration widget to 
        ``self.form``.
        """
        _next(self)
        if not has_permission('edit', self.model.parent, self.request):
            # XXX: yafowil expiration display renderer
            return
        expires_widget = factory(
            'field:label:expires',
            name='expires',
            props={
                'label': 'Expires',
            },
        )
        save_widget = self.form['save']
        self.form.insertbefore(expires_widget, save_widget)
    
    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)
        if not has_permission('manage', self.model.parent, self.request):
            return