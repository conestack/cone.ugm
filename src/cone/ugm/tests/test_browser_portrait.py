from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.user import UserEditForm
from cone.ugm.utils import general_settings
from io import BytesIO
from pyramid.view import render_view_to_response
import importlib


def user_portrait_request(layer, model, portrait):
    request = layer.new_request()
    request.params['ajax'] = '1'
    request.params['userform.password'] = '_NOCHANGE_'
    request.params['userform.portrait'] = portrait
    request.params['userform.principal_roles'] = []
    request.params['action.userform.save'] = '1'
    return request


def dummy_file_data(filename):
    with importlib.resources.path('yafowil.widget.image', 'testing') as base_path:
        path = base_path / filename
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
                settings.attrs.users_portrait = 'True'
                settings()

        return wrapper


class BrowserPortraitTests:
    @portrait_principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
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
            'src="http://example.com/resources/ugm/images/default_portrait.jpg?nocache='
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
        settings.attrs.users_portrait = 'False'
        settings()

        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertFalse(res.find('id="input-userform-portrait"') > -1)

    @testing.principals(users={'user_1': {}})
    def test_portrait_image(self):
        user = get_root()['users']['user_1']
        dummy_jpg = dummy_file_data('dummy.jpg')
        user.attrs['portrait'] = dummy_jpg
        user()
        request = self.layer.new_request()
        with self.layer.authenticated('user_1'):
            res = render_view_to_response(user, request, name='portrait_image')
        self.assertEqual(res.body, dummy_jpg)
        self.assertEqual(res.headers['Content-Type'], 'image/jpeg')
        self.assertEqual(res.headers['Cache-Control'], 'max-age=0')

    @testing.principals(users={'user_1': {}})
    def test_portrait_widget_without_edit_user(self):
        form = UserEditForm()
        form.model = get_root()['users']['user_1']
        form.request = self.layer.new_request()
        with self.layer.authenticated('user_1'):
            form.prepare()
        self.assertEqual(form.form['portrait'].mode, 'display')

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    @testing.invalidate_settings
    def test_save_portrait_disabled(self):
        general_settings(get_root()).attrs.users_portrait = 'False'
        user = get_root()['users']['user_1']
        portrait = {
            'file': BytesIO(dummy_file_data('dummy.jpg')),
            'mimetype': 'image/jpeg',
        }
        request = user_portrait_request(self.layer, user, portrait)
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertIsNone(user.attrs.get('portrait'))


class TestBrowserPortrait(TileTestCase, BrowserPortraitTests):
    layer = testing.ugm_layer

    @testing.principals(
        users={'manager': {}, 'user_1': {}}, roles={'manager': ['manager']}
    )
    def test_delete_portrait(self):
        # Not part of ``BrowserPortraitTests``: the SQL backend refuses to
        # delete user attributes
        user = get_root()['users']['user_1']
        user.attrs['portrait'] = dummy_file_data('dummy.jpg')
        user()
        request = user_portrait_request(self.layer, user, '')
        request.params['userform.portrait-action'] = 'delete'
        with self.layer.authenticated('manager'):
            render_tile(user, request, 'editform')
        user = get_root()['users']['user_1']
        self.assertIsNone(user.attrs.get('portrait'))
