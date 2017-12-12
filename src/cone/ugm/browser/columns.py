from cone.app.browser.layout import ProtectedContentTile
from cone.tile import Tile
from cone.tile import registerTile
from cone.tile import render_tile


registerTile(
    'content',
    'cone.ugm:browser/templates/columns.pt',
    class_=ProtectedContentTile,
    permission='login',
    strict=False
)


class Column(Tile):
    """Abstract column.
    """

    def _render(self, model, name):
        return render_tile(model, self.request, name)
