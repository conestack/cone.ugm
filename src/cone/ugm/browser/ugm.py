from cone.tile import tile, Tile
from cone.ugm.model.interfaces import IUgm
from cone.ugm.browser.columns import Column


# XXX: hack to display the site name
@tile('site', interface=IUgm, permission='view')
class SiteName(Tile):
    def render(self):
        if 'oshanet' in self.model['settings'].ldap_gcfg.baseDN:
            return "OSHANET"
        else:
            return "CORPORATE"


@tile('leftcolumn', interface=IUgm, permission='view')
class RootLeftColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'leftcolumn')


@tile('rightcolumn', interface=IUgm, permission='view')
class RootRightColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'rightcolumn')
