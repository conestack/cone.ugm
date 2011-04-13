from cone.tile import tile
from cone.ugm.model.interfaces import IUgm
from cone.ugm.browser.columns import Column


@tile('leftcolumn', interface=IUgm, permission='view')
class RootLeftColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'leftcolumn')


@tile('rightcolumn', interface=IUgm, permission='view')
class RootRightColumn(Column):
    
    def render(self):
        return self._render(self.model['users'], 'rightcolumn')