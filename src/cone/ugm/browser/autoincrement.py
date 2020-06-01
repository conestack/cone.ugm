from cone.ugm.utils import general_settings
from plumber import Behavior
from plumber import default
from plumber import plumb
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('cone.ugm')


class AutoIncrementForm(Behavior):
    """Plumbing behavior for setting user id by auto increment logic.

    For user add form.
    """

    @default
    @property
    def autoincrement_support(self):
        settings = general_settings(self.model)
        return settings.attrs.user_id_autoincrement == 'True'

    @default
    @property
    def next_principal_id(self):
        settings = general_settings(self.model)
        prefix = settings.attrs.user_id_autoincrement_prefix
        default = int(settings.attrs.user_id_autoincrement_start)
        search = u'%s*' % prefix
        backend = self.model.parent.backend
        backend.invalidate()
        result = backend.search(attrlist=['id'], criteria={'id': search})
        if result and isinstance(result[0][1]['id'], list):
            # XXX: is node.ext.ldap behavior attr list values are lists.
            #      keep until node.ext.ldap supports single valued fields.
            principlal_ids = [_[1]['id'][0] for _ in result]
        else:
            principlal_ids = [_[1]['id'] for _ in result]
        matching = list()
        for principal_id in principlal_ids:
            if prefix:
                principal_id = principal_id[len(prefix):]
            try:
                principal_id = int(principal_id)
            except ValueError:
                continue
            matching.append(principal_id)
        if not matching:
            principal_id = default
        else:
            principal_id = sorted(matching)[-1] + 1
        if principal_id < default:
            principal_id = default
        return u'%s%i' % (prefix, principal_id)

    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'id' disabled.
        """
        _next(self)
        if not self.autoincrement_support:
            return
        id_field = self.form['id']
        del id_field.attrs['required']
        id_field.attrs['disabled'] = 'disabled'
        id_field.getter = _('auto_incremented', default='auto incremented')

    @plumb
    def save(_next, self, widget, data):
        if self.autoincrement_support:
            data['id'].extracted = self.next_principal_id
        _next(self, widget, data)
