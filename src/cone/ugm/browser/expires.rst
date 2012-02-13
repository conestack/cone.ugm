Expiration widget
-----------------
  
Edit renderer::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<div class="expiration-widget"><input checked="checked" 
    id="checkbox-active" name="active.active" type="checkbox" 
    value="1" /><input class="datepicker expiration" id="input-active" 
    name="active" size="10" type="text" /></div>'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     value=0,
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<div class="expiration-widget"><input id="checkbox-active" 
    name="active.active" type="checkbox" value="1" /><input 
    class="datepicker expiration" id="input-active" name="active" 
    size="10" type="text" /></div>'
    
    >>> import datetime
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     value=datetime.datetime(2012, 01, 01),
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     })
    >>> widget()
    u'<div class="expiration-widget"><input checked="checked" 
    id="checkbox-active" name="active.active" type="checkbox" 
    value="1" /><input class="datepicker expiration" id="input-active" 
    name="active" size="10" type="text" value="1.1.2012" /></div>'

Display renderer::

    >>> from yafowil.base import factory
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<div class="expiration-widget"><input checked="checked" 
    disabled="disabled" id="checkbox-active" name="active.active" 
    type="checkbox" value="1" /></div>'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     value=0,
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<div class="expiration-widget"><input checked="checked" 
    disabled="disabled" id="checkbox-active" name="active.active" 
    type="checkbox" value="1" /></div>'
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
    ...     value=datetime.datetime(2012, 01, 01),
    ...     props={
    ...         'datepicker': True,
    ...         'locale': 'de',
    ...     },
    ...     mode='display')
    >>> widget()
    u'<div class="expiration-widget"><input checked="checked" 
    disabled="disabled" id="checkbox-active" name="active.active" 
    type="checkbox" value="1" /><div class="display-expiration" 
    id="display-active">2012.01.01 - 00:00</div></div>'

Extractor::
    
    >>> widget = factory(
    ...     'expiration',
    ...     name='active',
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
    ...     'active.active': '1',
    ...     'active': ''
    ... }
    >>> data = widget.extract(request)
    >>> data.extracted
    <UNSET>
    
    >>> request = {
    ...     'active.active': '1',
    ...     'active': '23.12.2012'
    ... }
    >>> data = widget.extract(request)
    >>> data.extracted
    1356217200.0
