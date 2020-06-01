from cone.ugm.browser.principal import email_field_factory
from cone.ugm.browser.principal import user_field
from pyramid.static import static_view


static_resources = static_view('static', use_subpath=True)


file_email_field_factory = user_field('mail', backend='file')(
    email_field_factory
)
