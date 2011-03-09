from cone.tile import Tile
from cone.ugm.browser.batch import ColumnBatch


class ColumnListing(Tile):
    """Abstract column listing.
    """
    
    current_id = None
    slot = None
    list_columns = []
    css = ''
    slicesize = 50
    batchname = ''
    
    @property
    def settings(self):
        return self.model.root['settings']
    
    @property
    def ajax_action(self):
        return 'columnlisting'
    
    @property
    def sortheader(self):
        ret = list()
        for id, name in self.list_columns:
            ret.append({
                'id': 'sort_%s' % id,
                'default': False,
                'name': name,
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
        items = self.query_items
        items = sorted(items, key=lambda x: x['sort_by'].lower())
        return items[start:end]
    
    @property
    def query_items(self):
        """Return list of dicts like:
        
        {
            'target': u'http://example.com/foo',
            'head': u'Head Column content',
            'sort_by: u'Sort value',
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
    
    def itemhead(self, col_1, col_2=None, col_3=None):
        head = '<div class="sort_col_1">%s&nbsp;</div>' % col_1
        if col_2 is not None:
            head += '<div class="sort_col_2">%s&nbsp;</div>' % col_2
        if col_3 is not None:
            head += '<div class="sort_col_3">&lt;%s&gt;</div>' % col_3
        return head
    
    def create_item(self, sort, target, head, current, actions):
        return {
            'sort_by': sort,
            'target': target,
            'head': head,
            'current': current,
            'actions': actions,
        }
    
    def create_action(self, id, enabled, title, target):
        return {
            'id': id,
            'enabled': enabled,
            'title': title,
            'target': target,
        }
    
    def extract_raw(self, attrs, name):
        raw = attrs.get(name)
        return raw and raw[0] or ''
    
    @property
    def user_attrs(self):
        settings = self.settings
        column_config = settings.attrs.users_listing_columns
        col_1_attr = column_config['col_1'].split(':')[0]
        col_2_attr = column_config['col_2'].split(':')[0]
        col_3_attr = column_config['col_3'].split(':')[0]
        sort_column = settings.attrs.users_listing_default_column
        sort_attr = column_config[sort_column]
        return col_1_attr, col_2_attr, col_3_attr, sort_attr
    
    @property
    def group_attrs(self):
        settings = self.settings
        column_config = settings.attrs.groups_listing_columns
        return column_config['col_1'].split(':')[0]
    
    @property
    def user_list_columns(self):
        settings = self.settings
        column_config = settings.attrs.users_listing_columns
        return [
            ('col_1', column_config['col_1'].split(':')[1]),
            ('col_2', column_config['col_2'].split(':')[1]),
            ('col_3', column_config['col_3'].split(':')[1]),
        ]
        
    @property
    def group_list_columns(self):
        settings = self.settings
        column_config = settings.attrs.groups_listing_columns
        return [
            ('col_1', column_config['col_1'].split(':')[1]),
        ]
