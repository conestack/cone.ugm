from cone.app import get_root
from cone.app.model import BaseNode
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.model.user import User
from cone.ugm.model.utils import ugm_general


def user_vessel(users):
    vessel = User(BaseNode(), None, None)
    vessel.__parent__ = users
    return vessel


def user_request(layer, cn, sn, mail):
    request = layer.new_request()
    request.params['userform.id'] = ''
    request.params['userform.userPassword'] = '123456'
    request.params['userform.cn'] = cn
    request.params['userform.sn'] = sn
    request.params['userform.mail'] = mail
    request.params['userform.principal_roles'] = ['viewer', 'editor']
    request.params['action.userform.save'] = '1'
    return request


class cleanup_autoincrement_test(testing.remove_principals):

    def __call__(self, fn):
        w = super(cleanup_autoincrement_test, self).__call__(fn)

        def wrapper(inst):
            w(inst)

            cfg = ugm_general(get_root())
            cfg.attrs.user_id_autoincrement = 'False'
            cfg.attrs.user_id_autoincrement_prefix = ''
            cfg()
        return wrapper


class TestBrowserAutoincrement(TileTestCase):
    layer = testing.ugm_layer

    @cleanup_autoincrement_test(users=['100', '101', 'uid100', 'uid101'])
    def test_autoincrement(self):
        root = get_root()
        users = root['users']

        cfg = ugm_general(users)
        self.assertEqual(cfg.attrs.user_id_autoincrement, 'False')
        self.assertEqual(cfg.attrs.user_id_autoincrement_prefix, '')

        vessel = user_vessel(users)
        request = self.layer.new_request()
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.checkOutput("""
        ...<input class="form-control required text" id="input-userform-id"
        name="userform.id" required="required" type="text" value="" />...
        """, res)

        cfg.attrs.user_id_autoincrement = 'True'
        cfg()

        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.checkOutput("""
        ...<input class="form-control text" disabled="disabled"
        id="input-userform-id" name="userform.id" type="text"
        value="auto_incremented" />...
        """, res)

        request = user_request(
            self.layer,
            'Sepp Unterwurzacher',
            'Sepp',
            'sepp@unterwurzacher.org'
        )
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', 'admin', 'editor', 'localmanager_1', 'localmanager_2',
            'manager', 'max', 'sepp', 'uid0', 'uid1', 'uid2', 'uid3',
            'uid4', 'uid5', 'uid6', 'uid7', 'uid8', 'uid9', 'viewer'
        ])

        request = user_request(
            self.layer,
            'Franz Hinterhuber',
            'Franz',
            'franz@hinterhuber.org'
        )
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', '101', 'admin', 'editor', 'localmanager_1', 'localmanager_2',
            'manager', 'max', 'sepp', 'uid0', 'uid1', 'uid2', 'uid3',
            'uid4', 'uid5', 'uid6', 'uid7', 'uid8', 'uid9', 'viewer'
        ])

        cfg.attrs.user_id_autoincrement_prefix = 'uid'
        cfg()
        request = user_request(
            self.layer,
            'Ander Er',
            'Ander',
            'ander@er.org'
        )
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', '101', 'admin', 'editor', 'localmanager_1', 'localmanager_2',
            'manager', 'max', 'sepp', 'uid0', 'uid1', 'uid100', 'uid2', 'uid3',
            'uid4', 'uid5', 'uid6', 'uid7', 'uid8', 'uid9', 'viewer'
        ])

        request = user_request(
            self.layer,
            'Hirs Schneider',
            'Hirs',
            'hirs@schneider.org'
        )
        vessel = user_vessel(users)
        with self.layer.authenticated('manager'):
            res = render_tile(vessel, request, 'addform')
        self.assertEqual(sorted(users.keys()), [
            '100', '101', 'admin', 'editor', 'localmanager_1', 'localmanager_2',
            'manager', 'max', 'sepp', 'uid0', 'uid1', 'uid100', 'uid101',
            'uid2', 'uid3', 'uid4', 'uid5', 'uid6', 'uid7', 'uid8', 'uid9',
            'viewer'
        ])
