from cone.app import get_root
from cone.app import security
from cone.app.browser.layout import personal_tools
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.password import ChangePasswordAction
from cone.ugm.browser.password import ChangePasswordForm


class TestBrowserPassword(TileTestCase):
    layer = testing.ugm_layer

    @testing.principals(
        users={
            'user_1': {}
        }
    )
    def test_ChangePasswordFormAction(self):
        self.assertIsInstance(
            personal_tools['change_password'],
            ChangePasswordAction
        )

        root = get_root()
        action = ChangePasswordAction()
        action.model = root['users']['user_1']
        action.request = self.layer.new_request()

        self.assertFalse(action.display)
        with self.layer.authenticated('superuser'):
            self.assertFalse(action.display)
        with self.layer.authenticated('user_1'):
            self.assertTrue(action.display)
            self.assertEqual(
                action.href,
                'http://example.com/users/user_1/change_password'
            )
            self.assertEqual(
                action.target,
                'http://example.com/users/user_1?contenttile=change_password'
            )

    @testing.principals(
        users={
            'user_1': {}
        }
    )
    def test_ChangePasswordForm(self):
        root = get_root()
        model = root['users']['user_1']
        form = ChangePasswordForm()
        form.model = model
        form.request = self.layer.new_request()

        self.assertFalse(form.show_contextmenu)
        with self.layer.authenticated('user_1'):
            self.assertEqual(form.form_heading, 'Change Password: user_1')

            model.attrs['fullname'] = 'User 1'
            self.assertEqual(form.form_heading, 'Change Password: User 1')

        form.prepare()
        self.checkOutput("""
        <class 'yafowil.base.Widget'>: change_password_form
          <class 'yafowil.base.Widget'>: current_password
          <class 'yafowil.base.Widget'>: new_password
          <class 'yafowil.base.Widget'>: confirm_password
          <class 'yafowil.base.Widget'>: change
        """, form.form.treerepr())

        request = self.layer.new_request()
        form.request = request

        request.params['change_password_form.current_password'] = ''
        request.params['change_password_form.new_password'] = ''
        request.params['change_password_form.confirm_password'] = ''
        request.params['action.change_password_form.change'] = '1'
        with self.layer.authenticated('user_1'):
            data = form.form.extract(request)
            self.assertEqual(
                data['current_password'].errors[0].msg,
                'no_password_given'
            )
            self.assertEqual(
                data['new_password'].errors[0].msg,
                'no_password_given'
            )
            self.assertEqual(
                data['confirm_password'].errors[0].msg,
                'no_password_given'
            )

        request.params['change_password_form.current_password'] = 'invalid'
        with self.layer.authenticated('user_1'):
            data = form.form.extract(request)
            self.assertEqual(
                data['current_password'].errors[0].msg,
                'wrong_password'
            )

        request.params['change_password_form.current_password'] = 'secret'
        request.params['change_password_form.new_password'] = '123456'
        request.params['change_password_form.confirm_password'] = '123457'
        with self.layer.authenticated('user_1'):
            data = form.form.extract(request)
            self.assertEqual(data['current_password'].errors, [])
            self.assertEqual(
                data['confirm_password'].errors[0].msg,
                'password_missmatch'
            )

        request.params['change_password_form.confirm_password'] = '123456'
        with self.layer.authenticated('user_1'):
            form(model, request)
            user = security.authenticated_user(request)
            self.assertTrue(user.authenticate('123456'))
