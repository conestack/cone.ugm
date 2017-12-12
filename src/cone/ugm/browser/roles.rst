Roles support
-------------

::

    >>> from cone.tile import render_tile
    >>> from cone.app import get_root
    >>> from cone.app.model import BaseNode
    >>> from cone.ugm.model.user import User
    >>> from cone.ugm.model.utils import ugm_users

    >>> layer.login('manager')

Cleanup::

    >>> layer.logout()
