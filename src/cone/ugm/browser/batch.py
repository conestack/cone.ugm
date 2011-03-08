from cone.app.browser.batch import Batch
from cone.app.browser.utils import (
    nodepath,
    make_query, 
    make_url,
)


class ColumnBatch(Batch):
    """Abstract UGM column batch.
    """
    
    def __init__(self, name, items, slicesize):
        self.name = name
        #self.name = 'columnbatch'
        self.path = None
        self.attribute = 'render'
        self.items = items
        self.slicesize = slicesize
    
    @property
    def display(self):
        return len(self.vocab) > 1
    
    @property
    def vocab(self):
        ret = list()
        path = nodepath(self.model)
        count = len(self.items)
        pages = count / self.slicesize
        if count % self.slicesize != 0:
            pages += 1
        current = self.request.params.get('b_page', '0')
        for i in range(pages):
            query = make_query(b_page=str(i))
            url = make_url(self.request, path=path, query=query)
            ret.append({
                'page': '%i' % (i + 1),
                'current': current == str(i),
                'visible': True,
                'url': url,
            })
        return ret
    
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