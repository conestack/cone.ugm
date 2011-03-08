from cone.tile import Tile
from cone.ugm.browser.batch import ColumnBatch


class ColumnListing(Tile):
    """Abstract column listing.
    """
    
    current_id = None
    slot = None
    list_columns = []
    css = ''
    slicesize = 10
    batchname = ''
    column = ''
    
    @property
    def ajax_action(self):
        return 'columnlisting'
    
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
    def batch(self):
        return ColumnBatch(self.batchname,
                           self.query_items,
                           self.slicesize)(self.model, self.request)
    
    @property
    def slice(self):
        current = int(self.request.params.get('b_page', '0'))
        start = current * self.slicesize
        end = start + self.slicesize
        return start, end
    
    @property
    def items(self):
        start, end = self.slice
        return self.query_items[start:end]
    
    @property
    def query_items(self):
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