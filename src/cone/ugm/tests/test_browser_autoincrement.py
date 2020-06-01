from cone.app import get_root
from cone.app.model import BaseNode
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.model.user import User
from cone.ugm.utils import general_settings


def user_vessel(users):
    vessel = User(BaseNode(), None, None)
    vessel.__parent__ = users
    return vessel


def user_request(layer):
    request = layer.new_request()
    request.params['userform.id'] = ''
    request.params['userform.password'] = '123456'
    request.params['userform.principal_roles'] = []
    request.params['action.userform.save'] = '1'
    return request


class autoincrement_principals(testing.principals):

    def __call__(self, fn):
        w = super(autoincrement_principals, self).__call__(fn)

        def wrapper(inst):
            try:
                w(inst)
            finally:
                settings = general_settings(get_root())
                settings.attrs.user_id_autoincrement = 'False'
                settings.attrs.user_id_autoincrement_prefix = ''
                settings()
        return wrapper


class TestBrowserAutoincrement(TileTestCase):
    layer = testing.ugm_layer

    @autoincrement_principals(
        users={
            'manager': {}
        },
        roles={
            'manager': ['manager']
        }
    )
    def test_autoincrement(self):
        root = get_root()
        users = root['users']

        settings = general_settings(users)
        self.assertEqual(settings.attrs.user_id_autoincrement, 'False')
        self.assertEqual(settings.attrs.user_id_autoincrement_prefix, '')

        vessel = user_vessel(users)
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.checkOutput("""
        ...<input class="form-control required text" id="input-userform-id"
        name="userform.id" required="required" type="text" value="" />...
        """, res)

        settings.attrs.user_id_autoincrement = 'True'
        settings()

        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.checkOutput("""
        ...<input class="form-control text" disabled="disabled"
        id="input-userform-id" name="userform.id" type="text"
        value="auto_incremented" />...
        """, res)

        request = user_request(self.layer)
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), ['100', 'manager'])

        request = user_request(self.layer)
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), ['100', '101', 'manager'])

        settings.attrs.user_id_autoincrement_prefix = 'uid'
        settings()
        request = user_request(self.layer)
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', '101', 'manager', 'uid100'
        ])

        request = user_request(self.layer)
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', '101', 'manager', 'uid100', 'uid101'
        ])
