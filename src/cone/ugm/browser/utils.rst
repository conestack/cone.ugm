cone.ugm.browser.utils
======================

::

    >>> from cone.ugm.browser.utils import quote_slash, unquote_slash
    >>> quoted = quote_slash('foo/bar')
    >>> quoted
    'foo__s_l_a_s_h__bar'

    >>> unquote_slash(quoted)
    'foo/bar'
