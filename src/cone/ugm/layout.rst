cone.ugm.layout
===============

Test imports::

    >>> from cone.ugm.layout import UGMLayout

Check layout properties::

    >>> layout = UGMLayout()
    >>> assert(layout.mainmenu is True)
    >>> assert(layout.mainmenu_fluid is False)
    >>> assert(layout.livesearch is False)
    >>> assert(layout.personaltools is True)
    >>> assert(layout.columns_fluid is False)
    >>> assert(layout.pathbar is True)
    >>> assert(layout.sidebar_left == [])
    >>> assert(layout.sidebar_left_grid_width == 0)
    >>> assert(layout.content_grid_width == 12)
