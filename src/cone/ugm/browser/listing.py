from cone.tile import Tile


class ColumnListing(Tile):
    """Abstract column listing.
    """
    
    current_id = None
    slot = None
    list_columns = []
    
    @property
    def sortheader(self):
        ret = list()
        for id in self.list_columns:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': id,
            })
        ret[0]['default'] = True
        return ret
    
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
    
    def _itemhead(self, name, surname=None, email=None):
        head = '<div class="sort_name">%s&nbsp;</div>' % name
        if surname is not None:
            head += '<div class="sort_surname">%s&nbsp;</div>' % surname
        if email is not None:
            head += '<div class="sort_email">&lt;%s&gt;</div>' % email
        return head