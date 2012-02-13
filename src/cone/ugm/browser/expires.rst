Expiration widget
-----------------
  
Edit renderer::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<input checked="checked" name="expires.active" type="checkbox" value="1" 
    /><input class="datepicker expiration" id="input-expires" name="expires" 
    size="10" type="text" />'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     value=0,
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<input name="expires.active" type="checkbox" value="1" /><input 
    class="datepicker expiration" id="input-expires" name="expires" size="10" 
    type="text" />'
    
    >>> import datetime
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     value=datetime.datetime(2012, 01, 01),
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<input checked="checked" name="expires.active" type="checkbox" value="1" 
    /><input class="datepicker expiration" id="input-expires" name="expires" 
    size="10" type="text" value="1.1.2012" />'

Display renderer::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<input checked="checked" disabled="disabled" name="expires.active" 
    type="checkbox" value="1" />'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     value=0,
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<input checked="checked" disabled="disabled" name="expires.active" 
    type="checkbox" value="1" />'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     value=datetime.datetime(2012, 01, 01),
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<input checked="checked" disabled="disabled" name="expires.active" 
    type="checkbox" value="1" /><div class="display-expiration" 
    id="display-expires">2012.01.01 - 00:00</div>'

Extractor::
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    
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
