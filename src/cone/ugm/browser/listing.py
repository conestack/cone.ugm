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
    
    def itemhead(self, name, surname=None, email=None):
        head = '<div class="sort_name">%s&nbsp;</div>' % name
        if surname is not None:
            head += '<div class="sort_surname">%s&nbsp;</div>' % surname
        if email is not None:
            head += '<div class="sort_email">&lt;%s&gt;</div>' % email
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
        name_attr = column_config['name']
        surname_attr = column_config['surname']
        email_attr = column_config['email']
        sort_column = settings.attrs.users_listing_default_column
        sort_attr = column_config[sort_column]
        return name_attr, surname_attr, email_attr, sort_attr
    
    @property
    def group_attrs(self):
        settings = self.settings
        column_config = settings.attrs.groups_listing_columns
        return column_config['name']
