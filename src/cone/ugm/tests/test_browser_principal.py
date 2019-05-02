# from cone.app import get_root
from cone.app.model import BaseNode
from cone.tile import Tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.principal import _form_field
from cone.ugm.browser.principal import default_form_field_factory
from cone.ugm.browser.principal import FormFieldFactoryProxy
from yafowil.base import factory


class TestBrowserPrincipal(TileTestCase):
    layer = testing.ugm_layer

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

        del _form_field.registry[SCOPE]
