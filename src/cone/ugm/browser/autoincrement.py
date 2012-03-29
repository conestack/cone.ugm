from plumber import (
    Part,
    default,
    plumb,
)
from pyramid.security import has_permission
from cone.ugm.model.utils import ugm_users


class AutoIncrementForm(Part):
    
    @default
    @property
    def autoincrement_support(self):
        ucfg = ugm_users(self.model)
        return ucfg.attrs['user_id_autoincrement'] == 'True'
    
    @plumb
    def prepare(_next, self):
        """Hook after prepare and set 'principal_roles' as selection to 
        ``self.form``.
        """
        _next(self)
        if not self.autoincrement_support:
            return
        if not has_permission('manage', self.model.parent, self.request):
            return
        import pdb;pdb.set_trace()
        
    
    @plumb
    def save(_next, self, widget, data):
        _next(self, widget, data)
        if not self.autoincrement_support:
            return
        if not has_permission('manage', self.model.parent, self.request):
            return


#    def uidNumber(node, uid):
#        """Default function gets called twice, second time without node.
#        
#        Bug. fix me.
#        
#        XXX: gets called by samba defaults
#        """
#        from node.ext.ldap.ugm import posix
#        if not node:
#            return posix.UID_NUMBER
#        existing = node.search(criteria={'uidNumber': '*'}, attrlist=['uidNumber'])
#        uidNumbers = [int(item[1]['uidNumber'][0]) for item in existing]
#        uidNumbers.sort()
#        if not len(uidNumbers):
#            return '100'
#        posix.UID_NUMBER = str(uidNumbers[-1] + 1)
#        return posix.UID_NUMBER