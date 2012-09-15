# XXX: temporary hack to enabled / in one url component


def quote_slash(x):
    return x.replace('/', '__s_l_a_s_h__')


def unquote_slash(x):
    return x.replace('__s_l_a_s_h__', '/')
