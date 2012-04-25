from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.i18n import TranslationStringFactory
from cone.ugm.model.utils import ugm_general

_ = TranslationStringFactory('cone.ugm')


class AutoIncrementForm(Part):
    """Plumbing part for setting user id by auto increment logic.
    
    For user add form.
    """
    
    @default
    @property
    def autoincrement_support(self):
        cfg = ugm_general(self.model)
        return cfg.attrs['user_id_autoincrement'] == 'True'
    
    @default
    @property
    def next_principal_id(self):
        cfg = ugm_general(self.model)
        prefix = cfg.attrs['user_id_autoincrement_prefix']
        default = int(cfg.attrs['user_id_autoincrement_start'])
        search = u'%s*' % prefix
        backend = self.model.parent.backend
        backend.invalidate()
        result = backend.search(attrlist=['id'], criteria={'id': search})
        principlal_ids = [_[1]['id'][0] for _ in result]
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
        id_field.getter = _('auto_incremented', 'auto incremented')
    
    @plumb
    def save(_next, self, widget, data):
        if self.autoincrement_support:
            data['id'].extracted = self.next_principal_id
        _next(self, widget, data)