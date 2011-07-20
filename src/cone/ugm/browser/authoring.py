from plumber import (
    plumb,
    Part,
)
from cone.app.browser.ajax import ajax_form_fiddle

class AddFormFiddle(Part):
    """Form fiddle plumbing part for user and group add forms.
    """
    
    @plumb
    def __call__(_next, self, model, request):
        ajax_form_fiddle(request, '.right_column', 'inner')
        return _next(self, model, request)


class EditFormFiddle(Part):
    """Form fiddle plumbing part for user and group edit forms.
    """
    
    @plumb
    def __call__(_next, self, model, request):
        ajax_form_fiddle(request, '.principal_form', 'inner')
        return _next(self, model, request)