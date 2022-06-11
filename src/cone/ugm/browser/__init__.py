from cone.app.browser.resources import resources
from cone.app.browser.resources import set_resource_include
import webresource as wr
import os


resources_dir = os.path.join(os.path.dirname(__file__), 'static')
cone_ugm_resources = wr.ResourceGroup(
    name='cone.ugm-ugm',
    directory=resources_dir,
    path='ugm',
    group=resources
)
cone_ugm_resources.add(wr.ScriptResource(
    name='cone-ugm-js',
#    depends='cone-app-protected-js',
    resource='cone.ugm.js',
    compressed='cone.ugm.min.js'
))
cone_ugm_resources.add(wr.StyleResource(
    name='cone-ugm-css',
    resource='cone.ugm.css'
))


def configure_resources(settings):
    set_resource_include(settings, 'cone-ugm-js', 'authenticated')
    set_resource_include(settings, 'cone-ugm-css', 'authenticated')
