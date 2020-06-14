from cone.app.browser.layout import ProtectedContentTile
from cone.tile import render_tile
from cone.tile import tile
from cone.tile import Tile
from cone.ugm.model.group import Group
from cone.ugm.model.groups import Groups
from cone.ugm.model.user import User
from cone.ugm.model.users import Users


@tile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    interface=Group,
    permission='login',
    strict=False)
@tile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    interface=Groups,
    permission='login',
    strict=False)
@tile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    interface=User,
    permission='login',
    strict=False)
@tile(
    name='content',
    path='cone.ugm:browser/templates/columns.pt',
    interface=Users,
    permission='login',
    strict=False)
class Columns(ProtectedContentTile):
    pass


class Column(Tile):
    """Abstract column.
    """

    def _render(self, model, name):
        return render_tile(model, self.request, name)
