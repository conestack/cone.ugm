import time
from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.security import has_permission
from yafowil.base import (
    factory,
    UNSET,
    fetch_value,
)
from yafowil.common import (
    generic_extractor,
    generic_required_extractor,
)
from yafowil.widget.datetime.widget import (
    datetime_edit_renderer,
    datetime_display_renderer,
    datetime_extractor,
)
from cone.ugm.model.utils import ugm_users


def expiration_extractor(widget, data):
    """Extract expiration information.
    
    - If active flag not set, Account is disabled (value 0).
    - If active flag set and value is UNSET, account never expires.
    - If active flag set and datetime choosen, account expires at given
      datetime.
    - Timestamp in seconds since epoch is returned. 
    """
    active = data.request.get('%s.active' % widget.name)
    if not active:
        return 0
    expires = data.extracted
    if expires:
        return time.mktime(expires.utctimetuple())
    return UNSET


def expiration_edit_renderer(widget, data):
    tag = data.tag
    active_attrs = dict()
    active_attrs['type'] = 'checkbox'
    active_attrs['name'] = '%s.active' % widget.name
    active_attrs['value'] = '1'
    value = fetch_value(widget, data)
    if value != 0:
        active_attrs['checked'] = 'checked'
    else:
        data.value = None
    active = tag('input', **active_attrs)
    expires = datetime_edit_renderer(widget, data)
    return active + expires


def expiration_display_renderer(widget, data):
    tag = data.tag
    active_attrs = dict()
    active_attrs['type'] = 'checkbox'
    active_attrs['name'] = '%s.active' % widget.name
    active_attrs['value'] = '1'
    active_attrs['checked'] = 'checked'
    active_attrs['disabled'] = 'disabled'
    active = tag('input', **active_attrs)
    expires = datetime_display_renderer(widget, data)
    return active + expires


factory.register(
    'expiration',
    extractors=[generic_extractor, generic_required_extractor,
                datetime_extractor, expiration_extractor], 
    edit_renderers=[expiration_edit_renderer],
    display_renderers=[expiration_display_renderer])


factory.doc['blueprint']['expiration'] = \
"""Add-on blueprint UGM expiration widget. Utilizes yafowil.widget.datetime.
"""

factory.defaults['expiration.class'] = 'expiration'

factory.defaults['expiration.datepicker_class'] = 'datepicker'

factory.defaults['expiration.format'] = '%Y.%m.%d - %H:%M'
factory.doc['props']['expiration.format'] = \
"""Pattern accepted by ``datetime.strftime``.
"""


class ExpirationForm(Part):
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set expiration widget to 
        ``self.form``.
        """
        _next(self)
        ucfg = ugm_users(self.model)
        enabled = ucfg.attrs['users_account_expiration'] == 'True'
        if not enabled:
            return
        mode = 'edit'
        if not has_permission('edit', self.model.parent, self.request):
            mode = 'display'
        if self.action_resource == 'edit':
            attr = ucfg.attrs['users_expires_attr']
            unit = int(ucfg.attrs['users_expires_unit'])
            value = int(self.model.attrs.get(attr, 0))
            if unit == 0:
                value /= 86400
        else:
            value = UNSET
        expires_widget = factory(
            'field:label:expires',
            name='expires',
            value=value,
            props={
                'label': 'Expires',
                'datepicker': True,
                'locale': 'de',
            },
            mode=mode
        )
        save_widget = self.form['save']
        self.form.insertbefore(expires_widget, save_widget)
    
    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)
        if not has_permission('manage', self.model.parent, self.request):
            return