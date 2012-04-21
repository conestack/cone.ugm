from StringIO import StringIO
from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.response import Response
from pyramid.security import has_permission
from pyramid.view import view_config
from yafowil.base import (
    factory,
    UNSET,
)
from cone.app.browser.utils import make_url
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_users


@view_config('portrait_image', context=User, permission='view')
def portrait_image(model, request):
    response = Response()
    ucfg = ugm_users(model)
    response.body = model.attrs[ucfg.attrs['users_portrait_attr']]
    response.headers['Content-Type'] = 'image/jpg'
    return response


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
        image_data = model.attrs.get(image_attr)
        if image_data:
            image_value = {'file': StringIO(image_data)}
            image_url = make_url(request, node=model, resource='portrait_image')
        else:
            image_value = UNSET
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
        if not self.portrait_support or \
          not has_permission('manage', self.model.parent, self.request):
            _next(self, widget, data)
            return
        ucfg = ugm_users(self.model)
        image_attr = ucfg.attrs['users_portrait_attr']
        portrait = data.fetch('userform.portrait').extracted
        if portrait:
            if portrait['action'] in ['new', 'replace']:
                self.model.attrs[image_attr] = portrait['file'].read()
            if portrait['action'] == 'delete':
                del self.model.attrs[image_attr]
        _next(self, widget, data)