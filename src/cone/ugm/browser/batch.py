from cone.tile import tile
from cone.app.browser.batch import Batch
from cone.ugm.model.users import Users
from cone.ugm.model.groups import Groups


class ColumnBatch(Batch):
    """Abstract UGM column batch.
    """
    
    @property
    def display(self):
        return True
    
    @property
    def vocab(self):
        # XXX: nothing senceful yet, dummy code for CSS
        ret = list()
        for char in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                     'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                     'Y', 'X', 'Y', 'Z', 5 * '&nbsp;' + 'ALL']:
            ret.append({
                'page': char,
                'current': False,
                'visible': True,
                'url': '',
            })
        ret[3]['visible'] = False
        ret[10]['current'] = True
        return ret
    
    # just want to dislpay the batch vocab, disable other UI elements.
    
    @property
    def firstpage(self):
        return None
    
    @property
    def prevpage(self):
        return None
    
    @property
    def nextpage(self):
        return None
    
    @property
    def lastpage(self):
        return None
    
    @property
    def leftellipsis(self):
        return ''

    @property
    def rightellipsis(self):
        return ''