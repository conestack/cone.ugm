from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.security import has_permission
from pyramid.view import view_config
from yafowil.base import (
    factory,
    UNSET,
)
from cone.app.browser.utils import make_url
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_users


@view_config('portrait_image', context=User)
def portrait_image(model, request):
    pass


class PortraitForm(Part):
    """Plumbing part for setting user portrait image.
    """
    
    @default
    @property
    def portrait_support(self):
        ucfg = ugm_users(self.model)
        return ucfg.attrs['users_portrait'] == 'True'
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'portrait' as image widget to 
        ``self.form``.
        """
        _next(self)
        if not self.portrait_support:
            return
        model = self.model
        request = self.request
        if has_permission('manage', model.parent, request):
            mode = 'edit'
        else:
            mode = 'display'
        ucfg = ugm_users(model)
        image_attr = ucfg.attrs['users_portrait_attr']
        image_value = model.attrs.get(image_attr, UNSET)
        if image_value:
            image_url = make_url(request, node=model, resource='portrait_image')
        else:
            resource = 'cone.ugm.static/images/default_portrait.jpg'
            image_url = make_url(request, node=model.root, resource=resource)
        portrait_widget = factory(
            'field:label:image',
            name='portrait',
            value=image_value,
            props={
                'label': 'Portrait',
                'src': image_url,
                'alt': u'Portrait',
            },
            mode=mode)
        save_widget = self.form['save']
        self.form.insertbefore(portrait_widget, save_widget)
    
    @plumb
    def save(_next, self, widget, data):
        if self.portrait_support:
            # XXX:
            pass
        _next(self, widget, data)