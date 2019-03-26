from cone.app.browser.layout import ProtectedContentTile
from cone.tile import render_tile
from cone.tile import tile
from cone.tile import Tile


@tile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    permission='login',
    strict=False)
class Columns(ProtectedContentTile):
    pass


class Column(Tile):
    """Abstract column.
    """

    def _render(self, model, name):
        return render_tile(model, self.request, name)
