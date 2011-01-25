from cone.tile import Tile

class ColumnListing(Tile):
    """Abstract column listing.
    """
    
    current_id = None
    slot = None
    
    @property
    def items(self):
        """Return list of dicts like:
        
        {
            'target': u'http://example.com/foo',
            'head': u'Head Column content',
            'current': False,
            'actions': [
                {
                    'id': 'action_id',
                    'enabled': True,
                    'title': 'Action Title',
                    'target': u'http://example.com/foo',
                }
            ],
        }
        """
        raise NotImplementedError(u"Abstract ``ColumnListing`` does not "
                                  u"implement ``items`` property")