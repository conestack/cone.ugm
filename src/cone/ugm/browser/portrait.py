from StringIO import StringIO
from cone.app.browser.utils import make_url
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_general
from plumber import Behavior
from plumber import default
from plumber import plumb
from pyramid.i18n import TranslationStringFactory
from pyramid.response import Response
from pyramid.security import has_permission
from pyramid.view import view_config
from yafowil.base import UNSET
from yafowil.base import factory


_ = TranslationStringFactory('cone.ugm')


@view_config(
    name='portrait_image',
    context=User,
    permission='view_portrait')
def portrait_image(model, request):
    """XXX: needs polishing. Return configured default portrait if not set
    on user.
    """
    response = Response()
    cfg = ugm_general(model)
    response.body = model.attrs[cfg.attrs['users_portrait_attr']]
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Cache-Control'] = 'max-age=0'
    return response


class PortraitForm(Behavior):
    """Plumbing behavior for setting user portrait image.
    """

    @default
    @property
    def portrait_support(self):
        cfg = ugm_general(self.model)
        return cfg.attrs['users_portrait'] == 'True'

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
        if has_permission('edit_user', model.parent, request):
            mode = 'edit'
        else:
            mode = 'display'
        cfg = ugm_general(model)
        image_attr = cfg.attrs['users_portrait_attr']
        image_accept = cfg.attrs['users_portrait_accept']
        image_width = int(cfg.attrs['users_portrait_width'])
        image_height = int(cfg.attrs['users_portrait_height'])
        image_data = model.attrs.get(image_attr)
        if image_data:
            image_value = {
                'file': StringIO(image_data),
                'mimetype': 'image/jpeg',
            }
            image_url = make_url(request, node=model,
                                 resource='portrait_image')
        else:
            image_value = UNSET
            resource = 'cone.ugm.static/images/default_portrait.jpg'
            image_url = make_url(request, node=model.root, resource=resource)
        portrait_widget = factory(
            'field:label:error:image',
            name='portrait',
            value=image_value,
            props={
                'label': _('portrait', default='Portrait'),
                'src': image_url,
                'alt': _('portrait', default='Portrait'),
                'accept': image_accept,
                'minsize': (image_width, image_height),
                'crop': {
                    'size': (image_width, image_height),
                    'fitting': True,
                }
            },
            mode=mode)
        save_widget = self.form['save']
        self.form.insertbefore(portrait_widget, save_widget)

    @plumb
    def save(_next, self, widget, data):
        if not self.portrait_support or \
                not has_permission('edit_user', self.model.parent, self.request):
            _next(self, widget, data)
            return
        cfg = ugm_general(self.model)
        image_attr = cfg.attrs['users_portrait_attr']
        portrait = data.fetch('userform.portrait').extracted
        if portrait:
            if portrait['action'] in ['new', 'replace']:
                cropped = portrait['cropped']
                image_data = StringIO()
                cropped.save(image_data, 'jpeg', quality=100)
                image_data.seek(0)
                self.model.attrs[image_attr] = image_data.read()
            if portrait['action'] == 'delete':
                del self.model.attrs[image_attr]
        _next(self, widget, data)
