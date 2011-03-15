from cone.tile import tile, Tile
from cone.app.model import AppRoot
from cone.ugm.model.utils import map_users_and_groups
from cone.ugm.browser.columns import Column
from cone.ugm.model.utils import ugm_settings


# XXX: hack to display the site name
@tile('site', interface=AppRoot, permission='view')
class SiteName(Tile):
    def render(self):
        # XXX: move this out
        # XXX: currently the ldap users and groups need to know
        # mutually about themselves. Feels like node.ext.ugm should
        # present us the combo.
        map_users_and_groups(self.model)
        settings = ugm_settings(self.model)
        if 'oshanet' in settings.ldap_gcfg.baseDN:
            return "OSHANET"
        else:
            return "CORPORATE"


@tile('leftcolumn', interface=AppRoot, permission='view')
class RootLeftColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'leftcolumn')


@tile('rightcolumn', interface=AppRoot, permission='view')
class RootRightColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'rightcolumn')
