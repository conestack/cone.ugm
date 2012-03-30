from plumber import (
    Part,
    default,
    plumb,
)
from cone.ugm.model.utils import ugm_users


class AutoIncrementForm(Part):
    """Plumbing part for setting user id by auto increment logic.
    
    For user add form.
    """
    
    @default
    @property
    def autoincrement_support(self):
        ucfg = ugm_users(self.model)
        return ucfg.attrs['user_id_autoincrement'] == 'True'
    
    @default
    @property
    def next_principal_id(self):
        ucfg = ugm_users(self.model)
        prefix = ucfg.attrs['user_id_autoincrement_prefix']
        default = int(ucfg.attrs['user_id_autoincrement_start'])
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
        id_field.getter = 'auto incremented'
    
    @plumb
    def save(_next, self, widget, data):
        if self.autoincrement_support:
            data['id'].extracted = self.next_principal_id
        _next(self, widget, data)