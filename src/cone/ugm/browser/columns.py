from cone.app.browser.layout import ProtectedContentTile
from cone.tile import registerTile
from cone.tile import render_tile
from cone.tile import Tile


registerTile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    class_=ProtectedContentTile,
    permission='login',
    strict=False
)


class Column(Tile):
    """Abstract column.
    """

    def _render(self, model, name):
        return render_tile(model, self.request, name)
