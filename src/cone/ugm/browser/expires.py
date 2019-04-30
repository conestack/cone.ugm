from cone.ugm.utils import general_settings
from datetime import datetime
from plumber import Behavior
from plumber import plumb
from pyramid.i18n import TranslationStringFactory
from yafowil.base import factory
from yafowil.base import fetch_value
from yafowil.base import UNSET
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.utils import cssid
from yafowil.widget.datetime.widget import datetime_display_renderer
from yafowil.widget.datetime.widget import datetime_extractor
from yafowil.widget.datetime.widget import format_date
from yafowil.widget.datetime.widget import format_time
from yafowil.widget.datetime.widget import render_datetime_input
import time


_ = TranslationStringFactory('cone.ugm')


def expiration_extractor(widget, data):
    """Extract expiration information.

    - If active flag not set, Account is disabled (value 0).
    - If active flag set and value is UNSET, account never expires.
    - If active flag set and datetime choosen, account expires at given
      datetime.
    - Timestamp in seconds since epoch is returned.
    """
    active = int(data.request.get('%s.active' % widget.name, '0'))
    if not active:
        return 0
    expires = data.extracted
    if expires:
        return time.mktime(expires.utctimetuple())
    return UNSET


def expiration_edit_renderer(widget, data):
    tag = data.tag
    active_attrs = dict()
    active_attrs['id'] = cssid(widget, 'checkbox')
    active_attrs['type'] = 'checkbox'
    active_attrs['name'] = '%s.active' % widget.name
    active_attrs['value'] = '1'
    value = fetch_value(widget, data)
    if value == 8639913600:
        value = UNSET
    if value != 0:
        active_attrs['checked'] = 'checked'
    active = tag('input', **active_attrs)
    until = tag('label', u'until')
    locale = widget.attrs['locale']
    if callable(locale):
        locale = locale(widget, data)
    date = None
    time = widget.attrs['time']
    if value in [0, UNSET]:
        date = ''
    else:
        date = datetime.fromtimestamp(value)
        if time:
            time = format_time(date)
        date = format_date(date, locale, widget.attrs['delimiter'])
    expires = render_datetime_input(widget, data, date, time)
    return tag('div', active + until + expires, class_='expiration-widget')


def expiration_display_renderer(widget, data):
    tag = data.tag
    active_attrs = dict()
    active_attrs['id'] = cssid(widget, 'checkbox')
    active_attrs['type'] = 'checkbox'
    active_attrs['disabled'] = 'disabled'
    value = data.value
    if value != 0:
        active_attrs['checked'] = 'checked'
    active = tag('input', **active_attrs)
    until = tag('label', u'until')
    if value not in [0, UNSET]:
        value = datetime.fromtimestamp(value)
    expires = datetime_display_renderer(widget, data, value)
    if expires:
        expires = until + expires
    return tag('div', active + expires, class_='expiration-widget')


factory.register(
    'expiration',
    extractors=[generic_extractor, generic_required_extractor,
                datetime_extractor, expiration_extractor],
    edit_renderers=[expiration_edit_renderer],
    display_renderers=[expiration_display_renderer])


factory.doc['blueprint']['expiration'] = \
"""Add-on blueprint UGM expiration widget. Utilizes yafowil.widget.datetime.
"""

factory.defaults['expiration.class'] = 'expiration form-control'

factory.defaults['expiration.datepicker_class'] = 'datepicker'

factory.defaults['expiration.datepicker'] = True

factory.defaults['expiration.time'] = False

factory.defaults['expiration.tzinfo'] = None

factory.defaults['expiration.delimiter'] = '.'

factory.defaults['expiration.locale'] = 'de'

factory.defaults['expiration.format'] = '%Y.%m.%d'
factory.doc['props']['expiration.format'] = \
"""Pattern accepted by ``datetime.strftime``.
"""


class ExpirationForm(Behavior):
    """Expiration field plumbing behavior for user forms.
    """

    @plumb
    def prepare(_next, self):
        """Hook after prepare and set expiration widget to
        ``self.form``.
        """
        _next(self)
        settings = general_settings(self.model)
        if settings.attrs.users_account_expiration != 'True':
            return
        mode = 'edit'
        if not self.request.has_permission(
                'manage_expiration', self.model.parent):
            mode = 'display'
        if self.action_resource == 'edit':
            attr = settings.attrs.users_expires_attr
            unit = int(settings.attrs.users_expires_unit)
            value = int(self.model.attrs.get(attr, 0))
            # if format days, convert to seconds
            if unit == 0:
                value *= 86400
        else:
            value = UNSET
        expires_widget = factory(
            'field:label:expiration',
            name='active',
            value=value,
            props={
                'label': _('active', default='Active')
            },
            mode=mode
        )
        save_widget = self.form['save']
        self.form.insertbefore(expires_widget, save_widget)

    @plumb
    def save(_next, self, widget, data):
        if self.request.has_permission(
                'manage_expiration', self.model.parent):
            settings = general_settings(self.model)
            if settings.attrs.users_account_expiration == 'True':
                attr = settings.attrs.users_expires_attr
                unit = int(settings.attrs.users_expires_unit)
                value = data.fetch('userform.active').extracted
                if value is UNSET:
                    if unit == 0:
                        value = 99999
                    else:
                        value = 8639913600
                elif value != 0:
                    if unit == 0:
                        add = 0
                        if value % 86400 != 0:
                            add = 1
                        value /= 86400
                        value += add
                    value = int(value)
                self.model.attrs[attr] = str(value)
        _next(self, widget, data)
