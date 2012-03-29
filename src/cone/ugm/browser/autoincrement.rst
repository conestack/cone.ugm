Autoincrement support::

   >>> from cone.app import get_root
   >>> from cone.ugm.model.utils import ugm_users
   
   >>> layer.login('manager')
   
   >>> root = get_root()
   >>> users = root['users']
   >>> user = users['uid0']
   
   >>> ucfg = ugm_users(user)
   >>> ucfg.attrs.user_id_autoincrement
   u'False'
   
   >>> ucfg.attrs.user_id_autoincrement_prefix
   u''
   
   >>> ucfg.attrs.user_id_autoincrement = u'True'
   >>> ucfg()
   
   >>> ucfg.attrs.user_id_autoincrement_prefix = u'user'
   >>> ucfg()

Cleanup::

   >>> ucfg.attrs.user_id_autoincrement = u'False'
   >>> ucfg.attrs.user_id_autoincrement_prefix = u''
   >>> ucfg()
   
   >>> layer.logout()
