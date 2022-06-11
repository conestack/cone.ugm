from cone.app.browser.resources import resources
from cone.app.browser.resources import set_resource_include
import webresource as wr
import os


resources_dir = os.path.join(os.path.dirname(__file__), 'static')

# cone ugm
cone_ugm_resources = wr.ResourceGroup(
    name='cone.ugm-ugm',
    directory=os.path.join(resources_dir, 'ugm'),
    path='ugm',
    group=resources
)
cone_ugm_resources.add(wr.ScriptResource(
    name='cone-ugm-js',
    depends='jquery-ugm-ui-js',
    resource='cone.ugm.js',
    compressed='cone.ugm.min.js'
))
cone_ugm_resources.add(wr.StyleResource(
    name='cone-ugm-css',
    depends='jquery-ugm-css',
    resource='cone.ugm.css'
))


def configure_resources(settings):
    # cone ugm
    set_resource_include(settings, 'cone-ugm-js', 'authenticated')
    set_resource_include(settings, 'cone-ugm-css', 'authenticated')
