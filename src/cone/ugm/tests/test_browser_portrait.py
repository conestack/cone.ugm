from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.utils import general_settings
from io import BytesIO
import pkg_resources


def user_portrait_request(layer, model, portrait):
    request = layer.new_request()
    request.params['ajax'] = '1'
    request.params['userform.password'] = '_NOCHANGE_'
    request.params['userform.portrait'] = portrait
    request.params['userform.principal_roles'] = []
    request.params['action.userform.save'] = '1'
    return request


def dummy_file_data(filename):
    path = pkg_resources.resource_filename(
        'yafowil.widget.image',
        'testing/{}'.format(filename)
    )
    with open(path, 'rb') as file:
        data = file.read()
    return data


class portrait_principals(testing.principals):

    def __call__(self, fn):
        w = super(portrait_principals, self).__call__(fn)

        def wrapper(inst):
            try:
                w(inst)
            finally:
                settings = general_settings(get_root())
                settings.attrs.users_portrait = u'True'
                settings()
        return wrapper


class TestBrowserPortrait(TileTestCase):
    layer = testing.ugm_layer

    @portrait_principals(
        users={
            'manager': {},
            'user_1': {}
        },
        roles={
            'manager': ['manager']
        })
    def test_portrait(self):
        root = get_root()
        users = root['users']
        user = users['user_1']

        # Portrait related config properties
        settings = general_settings(users)
        self.assertEqual(settings.attrs.users_portrait, 'True')
        self.assertEqual(settings.attrs.users_portrait_attr, 'portrait')
        self.assertEqual(settings.attrs.users_portrait_accept, 'image/jpeg')
        self.assertEqual(settings.attrs.users_portrait_width, '50')
        self.assertEqual(settings.attrs.users_portrait_height, '50')

        # Portrait enabled, widget is rendered
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertTrue(res.find('id="input-userform-portrait"') > -1)

        # No portrait, default portrait is shown
        expected = (
            'src="http://example.com/cone.ugm.static/images/'
            'default_portrait.jpg?nocache='
        )
        self.assertTrue(res.find(expected) > -1)

        # Submit portrait
        dummy_jpg = dummy_file_data('dummy.jpg')
        portrait = {
            'file': BytesIO(dummy_jpg),
            'mimetype': 'image/jpeg',
        }

        request = user_portrait_request(self.layer, user, portrait)
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')

        # New portrait set on user
        expected = b'\xff\xd8\xff\xe0\x00\x10JFIF'
        self.assertTrue(user.attrs['portrait'].startswith(expected))

        # Portrait present, link to user portrait is shown
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        expected = 'src="http://example.com/users/user_1/portrait_image?nocache='
        self.assertTrue(res.find(expected) > -1)

        # Portrait disabled, widget is skipped
        settings.attrs.users_portrait = u'False'
        settings()

        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertFalse(res.find('id="input-userform-portrait"') > -1)
