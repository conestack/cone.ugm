from cone.app.browser.batch import Batch
from cone.app.browser.utils import make_query
from cone.app.browser.utils import make_url
from cone.app.browser.utils import nodepath


class ColumnBatch(Batch):
    """UGM column batch.
    """

    def __init__(self, name, items, slicesize, term):
        self.name = name
        self.items = items
        self.slicesize = slicesize
        self.term = term

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
            query = make_query(b_page=str(i), term=self.term)
            url = make_url(self.request, path=path, query=query)
            ret.append({
                'page': '%i' % (i + 1),
                'current': current == str(i),
                'visible': True,
                'href': url,
                'target': url
            })
        return ret
