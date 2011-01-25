from repoze.bfg.view import static
from cone.app import browser
browser.MAIN_TEMPLATE = 'cone.ugm.browser:templates/main.pt'
browser.ADDITIONAL_CSS.append('cone.ugm.static/styles.css')

static_view = static('static')