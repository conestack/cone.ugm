from cone.ugm.utils import general_settings
from plumber import Behavior
from plumber import plumb
from pyramid.i18n import TranslationStringFactory
from yafowil.base import factory


_ = TranslationStringFactory('cone.ugm')


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
            'manage_expiration',
            self.model.parent
        ):
            mode = 'display'
        expires_widget = factory(
            'field:label:datetime',
            name='active',
            value=self.model.expires,
            props={
                'label': _('active', default='Active'),
                'datepicker': True,
                'time': False,
                'locale': 'de',
                'empty_value': None
            },
            mode=mode
        )
        save_widget = self.form['save']
        self.form.insertbefore(expires_widget, save_widget)

    @plumb
    def save(_next, self, widget, data):
        if self.request.has_permission(
            'manage_expiration',
            self.model.parent
        ):
            settings = general_settings(self.model)
            if settings.attrs.users_account_expiration == 'True':
                self.model.expires = data.fetch('userform.active').extracted
        _next(self, widget, data)
