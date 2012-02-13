Expiration widget
-----------------

Facturate expiration widget::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    
Edit renderer::

    >>> widget()
    u'<input checked="checked" name="expires.active" type="checkbox" value="1" 
    /><input class="datepicker expiration" id="input-expires" name="expires" 
    size="10" type="text" />'

Extractor::
    
    >>> request = {
    ... }
    >>> data = widget.extract(request)
    >>> data.extracted
    0
    
    >>> request = {
    ...     'expires.active': '1',
    ...     'expires': ''
    ... }
    >>> data = widget.extract(request)
    >>> data.extracted
    <UNSET>
    
    >>> request = {
    ...     'expires.active': '1',
    ...     'expires': '23.12.2012'
    ... }
    >>> data = widget.extract(request)
    >>> data.extracted
    1356217200.0