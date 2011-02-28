import pyramid_zcml
from pyramid.config import Configurator
from cone.ugm.model import get_root


def app(global_config, **settings):
    """ This function returns a WSGI application.
    """
    zcml_file = settings.get('configure_zcml', 'configure.zcml')
    config = Configurator(
        root_factory=get_root,
        settings=settings,
        autocommit=True)
    config.include(pyramid_zcml)
    config.begin()
    config.load_zcml(zcml_file)
    config.end()
    return config.make_wsgi_app()