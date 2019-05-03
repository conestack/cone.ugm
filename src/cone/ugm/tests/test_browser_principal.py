from cone.app import get_root
from cone.app.model import BaseNode
from cone.tile import Tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.principal import _form_field
from cone.ugm.browser.principal import default_form_field_factory
from cone.ugm.browser.principal import default_required_message
from cone.ugm.browser.principal import FormFieldFactoryProxy
from cone.ugm.browser.principal import group_field
from cone.ugm.browser.principal import group_id_field_factory
from cone.ugm.browser.principal import GroupExistsExtractor
from cone.ugm.browser.principal import login_name_field_factory
from cone.ugm.browser.principal import LoginNameExtractor
from cone.ugm.browser.principal import PrincipalExistsExtractor
from cone.ugm.browser.principal import PrincipalIdFieldFactory
from cone.ugm.browser.principal import user_field
from cone.ugm.browser.principal import user_id_field_factory
from cone.ugm.browser.principal import UserExistsExtractor
from cone.ugm.utils import general_settings
from node.utils import UNSET
from pyramid.i18n import get_localizer
from yafowil.base import ExtractionError
from yafowil.base import factory
from yafowil.common import ascii_extractor


class TestBrowserPrincipal(TileTestCase):
    layer = testing.ugm_layer

    def test_default_required_message(self):
        request = self.layer.new_request()
        # use inexistent locale to ensure message catalog bypass
        request._LOCALE_ = 'foo'
        message = default_required_message(request, 'Name')
        localizer = get_localizer(request)
        self.assertEqual(localizer.translate(message), 'No Name defined')

    def test_default_form_field_factory(self):
        form = Tile()
        label = 'Field Label'
        value = 'Field Value'
        container = factory('compound', name='container')
        container['field'] = default_form_field_factory(form, label, value)
        self.assertEqual(container(), (
            '<div class="form-group" id="field-container-field">'
            '<label class="control-label" for="input-container-field">Field Label</label>'
            '<input class="form-control text" id="input-container-field" '
            'name="container.field" type="text" value="Field Value" /></div>'
        ))

    def test_FormFieldFactoryProxy(self):
        def form_field_factory(form, label, value):
            return 'FACTORY_CALLED'

        factory = FormFieldFactoryProxy(form_field_factory, 'attr')
        self.assertEqual(factory.attr, 'attr')

        form = Tile()
        label = 'Field Label'
        value = 'Field Value'
        self.assertEqual(factory(form, label, value), 'FACTORY_CALLED')

    def test__form_field(self):
        self.expectError(AssertionError, _form_field, 'field')
        self.expectError(AssertionError, _form_field.factory, 'field')

        SCOPE = 'form'
        _form_field.registry[SCOPE] = {}

        class form_field(_form_field):
            scope = SCOPE

        @form_field('field')
        def form_field_factory(form, label, value):
            pass

        @form_field('attr_field', attr='attr')
        def attr_form_field_factory(form, label, value):
            pass

        @form_field('field', backend='backend')
        def backend_form_field_factory(form, label, value):
            pass

        @form_field('attr_field', attr='attr', backend='backend')
        def backend_attr_form_field_factory(form, label, value):
            pass

        self.assertEqual(_form_field.registry[SCOPE], {
            '__all_backends__': {
                'field': (form_field_factory, None),
                'attr_field': (attr_form_field_factory, 'attr')
            },
            'backend': {
                'field': (backend_form_field_factory, None),
                'attr_field': (backend_attr_form_field_factory, 'attr')
            }
        })

        factory = form_field.factory('field')
        self.assertEqual(factory.attr, None)
        self.assertEqual(factory.factory, form_field_factory)

        factory = form_field.factory('attr_field')
        self.assertEqual(factory.attr, 'attr')
        self.assertEqual(factory.factory, attr_form_field_factory)

        factory = form_field.factory('field', backend='backend')
        self.assertEqual(factory.attr, None)
        self.assertEqual(factory.factory, backend_form_field_factory)

        factory = form_field.factory('attr_field', backend='backend')
        self.assertEqual(factory.attr, 'attr')
        self.assertEqual(factory.factory, backend_attr_form_field_factory)

        factory = form_field.factory('field', backend='other')
        self.assertEqual(factory.attr, None)
        self.assertEqual(factory.factory, form_field_factory)

        factory = form_field.factory('attr_field', backend='other')
        self.assertEqual(factory.attr, 'attr')
        self.assertEqual(factory.factory, attr_form_field_factory)

        del _form_field.registry[SCOPE]

    def test_PrincipalExistsExtractor(self):
        # Abstract error_message
        extractor = PrincipalExistsExtractor(BaseNode())
        self.expectError(NotImplementedError, extractor.error_message, 'pid')

        # dummy model
        class Principals(BaseNode):
            backend = {'pid': object()}

        # dummy extractor
        class MyPrincipalExistsExtractor(PrincipalExistsExtractor):
            def error_message(self, principal_id):
                return 'Principal {} already exists'.format(principal_id)

        # principals container, add model and form widget
        principals = Principals(name='principals')
        add_model = BaseNode(parent=principals)
        extractor = MyPrincipalExistsExtractor(add_model)
        widget = factory(
            '*exists:text',
            name='principal_id',
            custom={'exists': {'extractors': [extractor]}}
        )

        # test already exists
        request = {'principal_id': 'pid'}
        data = widget.extract(request=request)
        self.assertTrue(data.has_errors)
        self.assertEqual(
            data.errors,
            [ExtractionError('Principal pid already exists')]
        )

        # test not already exists
        request = {'principal_id': 'new_pid'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'new_pid')

    @testing.temp_principals(users={'user_exists': {
        'sn': 'User Exists',
        'cn': 'User Exists'
    }})
    def test_UserExistsExtractor(self, users, groups):
        add_model = BaseNode(parent=users)
        extractor = UserExistsExtractor(add_model)
        widget = factory(
            '*exists:text',
            name='user_id',
            custom={'exists': {'extractors': [extractor]}}
        )

        # test already exists
        request = {'user_id': 'user_exists'}
        data = widget.extract(request=request)
        self.assertTrue(data.has_errors)
        self.assertEqual(
            data.errors,
            [ExtractionError('user_already_exists')]
        )

        # test not already exists
        request = {'user_id': 'new_user_id'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'new_user_id')

    @testing.temp_principals(groups={'group_exists': {}})
    def test_GroupExistsExtractor(self, users, groups):
        add_model = BaseNode(parent=groups)
        extractor = GroupExistsExtractor(add_model)
        widget = factory(
            '*exists:text',
            name='group_id',
            custom={'exists': {'extractors': [extractor]}}
        )

        # test already exists
        request = {'group_id': 'group_exists'}
        data = widget.extract(request=request)
        self.assertTrue(data.has_errors)
        self.assertEqual(
            data.errors,
            [ExtractionError('group_already_exists')]
        )

        # test not already exists
        request = {'group_id': 'new_group_id'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'new_group_id')

    def test_PrincipalIdFieldFactory(self):
        class PrincipalAddForm(Tile):
            action_resource = 'add'

        class PrincipalEditForm(Tile):
            action_resource = 'edit'

        factory = PrincipalIdFieldFactory(PrincipalExistsExtractor)

        # principal add form
        form = PrincipalAddForm()
        form.model = BaseNode()
        form.request = self.layer.new_request()
        widget = factory(form, 'Principal ID', UNSET)
        self.assertEqual(widget.getter, UNSET)
        self.assertEqual(widget.properties, {
            'required': 'no_field_value_defined',
            'ascii': True
        })
        self.assertEqual(
            widget.custom['ascii']['extractors'],
            [ascii_extractor]
        )
        self.assertTrue(isinstance(
            widget.custom['exists']['extractors'][0],
            PrincipalExistsExtractor
        ))
        self.assertEqual(widget.mode, 'edit')

        # principal edit form
        form = PrincipalEditForm()
        form.model = BaseNode()
        form.request = self.layer.new_request()
        widget = factory(form, 'Principal ID', 'pid')
        self.assertEqual(widget.getter, 'pid')
        self.assertEqual(widget.properties, {
            'required': 'no_field_value_defined',
            'ascii': True
        })
        self.assertEqual(
            widget.custom['ascii']['extractors'],
            [ascii_extractor]
        )
        self.assertTrue(isinstance(
            widget.custom['exists']['extractors'][0],
            PrincipalExistsExtractor
        ))
        self.assertEqual(widget.mode, 'display')

    def test_user_id_field_factory(self):
        factory = user_field.factory('id')
        self.assertEqual(factory.attr, None)
        self.assertTrue(isinstance(factory.factory, PrincipalIdFieldFactory))
        self.assertEqual(factory.factory, user_id_field_factory)
        self.assertEqual(
            factory.factory.principal_exists_extractor,
            UserExistsExtractor
        )

    def test_group_id_field_factory(self):
        factory = group_field.factory('id')
        self.assertEqual(factory.attr, None)
        self.assertTrue(isinstance(factory.factory, PrincipalIdFieldFactory))
        self.assertEqual(factory.factory, group_id_field_factory)
        self.assertEqual(
            factory.factory.principal_exists_extractor,
            GroupExistsExtractor
        )

    def test_LoginNameExtractor(self):
        # dummy backend
        class UsersBackend(object):
            def search(self, criteria):
                if criteria['login_attr'] == 'Login Name':
                    return ['user_name']

        # dummy model
        class Users(BaseNode):
            backend = UsersBackend()

        # adding. users container, add model and form widget
        users = Users(name='users')
        add_model = BaseNode(parent=users)
        extractor = LoginNameExtractor(add_model, 'login_attr')
        widget = factory(
            '*login:text',
            name='login_name',
            custom={'login': {'extractors': [extractor]}}
        )

        # test already exists
        request = {'login_name': 'Login Name'}
        data = widget.extract(request=request)
        self.assertTrue(data.has_errors)
        self.assertEqual(
            data.errors,
            [ExtractionError('user_login_not_unique')]
        )

        # test not already exists
        request = {'login_name': 'Other Login Name'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'Other Login Name')

        # test empty login name
        request = {'login_name': ''}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, '')

        # editing. users container, edit model and form widget
        edit_model = BaseNode(name='user_name', parent=users)
        extractor = LoginNameExtractor(edit_model, 'login_attr')
        widget = factory(
            '*login:text',
            name='login_name',
            custom={'login': {'extractors': [extractor]}}
        )

        # test login name belongs to edited node
        request = {'login_name': 'Login Name'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'Login Name')

        request = {'login_name': 'Other Login Name'}
        data = widget.extract(request=request)
        self.assertFalse(data.has_errors)
        self.assertEqual(data.extracted, 'Other Login Name')

        # test login name belongs to another user
        edit_model.__name__ = 'other_user_name'
        request = {'login_name': 'Login Name'}
        data = widget.extract(request=request)
        self.assertTrue(data.has_errors)
        self.assertEqual(
            data.errors,
            [ExtractionError('user_login_not_unique')]
        )

    @testing.invalidate_settings
    def test_login_name_field_factory(self):
        factory = user_field.factory('login')
        self.assertEqual(factory.attr, None)
        self.assertEqual(factory.factory, login_name_field_factory)

        users = get_root()['users']
        user = BaseNode(name='user', parent=users)
        form = Tile()
        form.model = user
        form.request = self.layer.new_request()

        settings = general_settings(users)
        settings.attrs.users_reserved_attrs = {
            'id': 'id',
            'login': 'id'
        }

        widget = factory(form, 'Login Name', UNSET)
        self.assertEqual(widget.getter, UNSET)
        self.assertEqual(widget.properties, {
            'label': 'Login Name'
        })
        self.assertTrue(isinstance(
            widget.custom['login']['extractors'][0],
            LoginNameExtractor
        ))
        self.assertEqual(widget.mode, 'skip')

        settings.attrs.users_reserved_attrs = {
            'id': 'id',
            'login': 'login'
        }
        widget = factory(form, 'Login Name', UNSET)
        self.assertEqual(widget.mode, 'edit')
