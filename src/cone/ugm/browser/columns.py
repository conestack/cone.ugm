from cone.tile import (
    Tile,
    registerTile,
    render_tile,
)
from cone.app.browser.layout import ProtectedContentTile


registerTile('content',
             'cone.ugm:browser/templates/columns.pt',
             class_=ProtectedContentTile,
             permission='login',
             strict=False)


class Column(Tile):
    """Abstract column.
    """
    
    def _render(self, model, name):
        return render_tile(model, self.request, name)