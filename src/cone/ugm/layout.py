from cone.app.model import Layout


class UGMLayout(Layout):

    def __init__(self, model=None):
        super(UGMLayout, self).__init__(model=model)
        self.mainmenu = True
        self.mainmenu_fluid = False
        self.livesearch = False
        self.personaltools = True
        self.columns_fluid = False
        self.pathbar = False
        self.sidebar_left = []
        self.sidebar_left_grid_width = 0
        self.content_grid_width = 12
