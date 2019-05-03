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
    request.params['userform.cn'] = model.attrs['cn']
    request.params['userform.sn'] = model.attrs['sn']
    request.params['userform.portrait'] = portrait
    request.params['userform.principal_roles'] = ['viewer', 'editor']
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


class cleanup_portrait_test(testing.temp_principals):

    def __call__(self, fn):
        w = super(cleanup_portrait_test, self).__call__(fn)

        def wrapper(inst):
            w(inst)

            settings = general_settings(get_root())
            settings.attrs.users_portrait = u'True'
            settings()
        return wrapper


class TestBrowserPortrait(TileTestCase):
    layer = testing.ugm_layer

    @cleanup_portrait_test(users={'uid99': {'cn': 'Uid99', 'sn': 'Uid99'}})
    def test_portrait(self, users, groups):
        user = users['uid99']

        # Portrait related config properties
        settings = general_settings(users)
        self.assertEqual(settings.attrs.users_portrait, 'True')
        self.assertEqual(settings.attrs.users_portrait_attr, 'jpegPhoto')
        self.assertEqual(settings.attrs.users_portrait_accept, 'image/jpeg')
        self.assertEqual(settings.attrs.users_portrait_width, '50')
        self.assertEqual(settings.attrs.users_portrait_height, '50')

        # Portrait enabled, widget is rendered
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertTrue(res.find('id="input-userform-portrait"') > -1)

        # No portrait, default portrait is shown
        expected = 'src="http://example.com/cone.ugm.static/images/default_portrait.jpg?nocache='
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
        self.assertTrue(user.attrs['jpegPhoto'].startswith(b'\xff\xd8\xff\xe0\x00\x10JFIF'))

        # Portrait present, link to user portrait is shown
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        expected = 'src="http://example.com/users/uid99/portrait_image?nocache='
        self.assertTrue(res.find(expected) > -1)

        # Portrait disabled, widget is skipped
        settings.attrs.users_portrait = u'False'
        settings()

        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(user, request, 'editform')
        self.assertFalse(res.find('id="input-userform-portrait"') > -1)
