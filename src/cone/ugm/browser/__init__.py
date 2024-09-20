import webresource as wr
import os


resources_dir = os.path.join(os.path.dirname(__file__), 'static')
cone_ugm_resources = wr.ResourceGroup(
    name='cone.ugm-ugm',
    directory=resources_dir,
    path='ugm'
)
cone_ugm_resources.add(wr.ScriptResource(
    name='cone-ugm-js',
    depends='cone-app-js',
    resource='cone.ugm.js',
    compressed='cone.ugm.min.js'
))
cone_ugm_resources.add(wr.StyleResource(
    name='cone-ugm-css',
    resource='cone.ugm.css'
))


def configure_resources(config, settings):
    config.register_resource(cone_ugm_resources)
    config.set_resource_include('cone-ugm-js', 'authenticated')
    config.set_resource_include('cone-ugm-css', 'authenticated')
