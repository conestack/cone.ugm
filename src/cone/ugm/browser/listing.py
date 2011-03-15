from yafowil.utils import Tag
from cone.tile import Tile
from cone.ugm.browser.batch import ColumnBatch
from cone.ugm.model.utils import ugm_settings

tag = Tag(lambda x: x)

class ColumnListing(Tile):
    """Abstract column listing.
    """

    current_id = None
    slot = None
    list_columns = []
    css = ''
    # XXX: Batch is effectively disabled, if enabled, the sorting
    # needs to be fixed before slicing
    slicesize = 100000
    batchname = ''

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
            'content': u'Head Column content',
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

    def item_content(self, *args):
        ret = u''
        pt = 0
        for arg in args:
            pt += 1
            ret += tag('div', '%s&nbsp;' % arg, class_='sort_col_%i' % pt)
        return ret

    def create_item(self, sort, target, content, current, actions):
        return {
            'sort_by': sort,
            'target': target,
            'content': content,
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
        settings = ugm_settings(self.model)
        column_config = settings.attrs.users_listing_columns
        ret = list()
        for i in range(3):
            attr = column_config['col_%i' % (i + 1)].split(':')[0]
            ret.append(attr)
        sort_column = settings.attrs.users_listing_default_column
        sort_attr = column_config[sort_column]
        ret.append(sort_attr)
        return ret

    @property
    def group_attrs(self):
        settings = ugm_settings(self.model)
        column_config = settings.attrs.groups_listing_columns
        return column_config['col_1'].split(':')[0]

    @property
    def user_list_columns(self):
        settings = ugm_settings(self.model)
        column_config = settings.attrs.users_listing_columns
        ret = list()
        for i in range(3):
            ret.append(('col_%i' % (i + 1),
                        column_config['col_%i' % (i + 1)].split(':')[1]))
        return ret

    @property
    def group_list_columns(self):
        settings = ugm_settings(self.model)
        column_config = settings.attrs.groups_listing_columns
        return [
            ('col_1', column_config['col_1'].split(':')[1]),
        ]
