Expiration widget
-----------------

::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='expires',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    
    >>> widget
    <Widget object 'expires' at ...>
    
    >>> widget()
    u'<input checked="checked" name="expires.active" type="checkbox" value="1" 
    /><input class="datepicker expiration" id="input-expires" name="expires" 
    size="10" type="text" />'