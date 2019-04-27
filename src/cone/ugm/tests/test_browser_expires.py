from cone.tile.tests import TileTestCase
from cone.ugm import testing
from node.utils import UNSET
from yafowil.base import factory


class TestBrowserExpires(TileTestCase):
    layer = testing.ugm_layer

    def test_expiration_widget(self):
        # Edit renderer. Active with no expiration date by default
        widget = factory(
            'expiration',
            name='active',
            props={
                'datepicker': True,
                'locale': 'de',
            })
        self.checkOutput("""
        <div class="expiration-widget"><input checked="checked"
        id="checkbox-active" name="active.active" type="checkbox"
        value="1" /><label>until</label><input class="datepicker expiration
        form-control" id="input-active" name="active" size="10" type="text"
        value="" /></div>
        """, widget())

        # Active with no expiration date
        request = dict()
        request['active.active'] = '1'
        request['active'] = ''
        data = widget.extract(request)
        self.assertEqual(data.extracted, UNSET)

        self.checkOutput("""
        <div class="expiration-widget"><input checked="checked"
        id="checkbox-active" name="active.active" type="checkbox"
        value="1" /><label>until</label><input class="datepicker expiration
        form-control" id="input-active" name="active" size="10" type="text"
        value="" /></div>
        """, widget(request=request))

        # Inactive
        request = dict()
        request['active.active'] = '0'
        request['active'] = ''
        data = widget.extract(request)
        self.assertEqual(data.extracted, 0)

        # Active with expiration date
        request = dict()
        request['active.active'] = '1'
        request['active'] = '23.12.2012'
        data = widget.extract(request)
        self.assertEqual(data.extracted, 1356217200.0)

        # Edit renderer with preset value
        widget = factory(
            'expiration',
            name='active',
            value=0,
            props={
                'datepicker': True,
                'locale': 'de',
            })
        self.checkOutput("""
        <div class="expiration-widget"><input id="checkbox-active"
        name="active.active" type="checkbox" value="1" /><label>until</label><input
        class="datepicker expiration form-control" id="input-active" name="active"
        size="10" type="text" value="" /></div>
        """, widget())

        widget = factory(
            'expiration',
            name='active',
            value=1356217200.0,
            props={
                'datepicker': True,
                'locale': 'de',
            })
        self.checkOutput("""
        <div class="expiration-widget"><input checked="checked"
        id="checkbox-active" name="active.active" type="checkbox"
        value="1" /><label>until</label><input class="datepicker expiration
        form-control" id="input-active" name="active" size="10" type="text"
        value="23.12.2012" /></div>
        """, widget())

        # Display renderer
        widget = factory(
            'expiration',
            name='active',
            props={
                'datepicker': True,
                'locale': 'de',
            },
            mode='display')
        self.checkOutput("""
        <div class="expiration-widget"><input checked="checked"
        disabled="disabled" id="checkbox-active"
        type="checkbox" /></div>
        """, widget())

        widget = factory(
            'expiration',
            name='active',
            value=0,
            props={
                'datepicker': True,
                'locale': 'de',
            },
            mode='display')
        self.checkOutput("""
        <div class="expiration-widget"><input disabled="disabled"
        id="checkbox-active" type="checkbox" /></div>
        """, widget())

        widget = factory(
            'expiration',
            name='active',
            value=1356217200.0,
            props={
                'datepicker': True,
                'locale': 'de',
                'format': '%Y.%m.%d',
            },
            mode='display')
        self.checkOutput("""
        <div class="expiration-widget"><input checked="checked"
        disabled="disabled" id="checkbox-active"
        type="checkbox" /><label>until</label><div class="display-expiration
        form-control" id="display-active">2012.12.23</div></div>
        """, widget())
