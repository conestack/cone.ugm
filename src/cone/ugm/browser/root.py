from cone.tile import tile, Tile
from cone.app.model import AppRoot
from cone.ugm.browser.columns import Column


@tile(name='site', interface=AppRoot, permission='view')
class SiteName(Tile):
    def render(self):
        # XXX: make site name configurable
        # settings = ugm_settings(self.model)
        # if 'oshanet' in settings.ldap_gcfg.baseDN:
        #     return "OSHANET"
        # else:
        #     return "CORPORATE"
        return 'SITENAME'


@tile(name='leftcolumn', interface=AppRoot, permission='view')
class RootLeftColumn(Column):

    def render(self):
        return self._render(self.model['users'], 'leftcolumn')


@tile(name='rightcolumn', interface=AppRoot, permission='view')
class RootRightColumn(Column):

    def render(self):
        return self._render(self.model['users'], 'rightcolumn')
