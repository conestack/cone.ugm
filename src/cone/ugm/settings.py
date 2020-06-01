from cone.app.model import BaseNode
from cone.app.model import Metadata
from cone.app.model import Properties
from cone.app.model import XMLProperties
from cone.ugm.localmanager import LocalManagerConfigAttributes
from cone.ugm.utils import general_settings
from node.utils import instance_property
from pyramid.i18n import TranslationStringFactory
import os


_ = TranslationStringFactory('cone.ugm')


ugm_cfg = Properties()
ugm_cfg.ugm_settings = ''
ugm_cfg.lm_settings = ''

# XXX: move cone.ugm.model.factory_defaults here


class UGMSettings(BaseNode):
    config_file = None

    def __call__(self):
        self.attrs()

    @instance_property
    def attrs(self):
        config_file = self.config_file
        if not os.path.isfile(config_file):
            msg = 'Configuration file {} not exists.'.format(config_file)
            raise ValueError(msg)
        return XMLProperties(config_file)

    def invalidate(self, attrs=[]):
        attrs.append('attrs')
        for attr in attrs:
            _attr = '_{}'.format(attr)
            if hasattr(self, _attr):
                delattr(self, _attr)


class GeneralSettings(UGMSettings):

    @property
    def config_file(self):
        return ugm_cfg.ugm_settings

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'ugm_settings_node',
            default='UGM Settings')
        metadata.description = _(
            'ugm_settings_node_description',
            default='General user and group management settings'
        )
        return metadata


class LocalManagerSettings(BaseNode):

    def attributes_factory(self, name=None, parent=None):
        return LocalManagerConfigAttributes(ugm_cfg.lm_settings)

    @instance_property
    def metadata(self):
        metadata = Metadata()
        metadata.title = _(
            'localmanager_settings_node',
            default='Local Manager Settings'
        )
        metadata.description = _(
            'localmanager_settings_node_description',
            default='Local Manager Settings'
        )
        return metadata

    @property
    def enabled(self):
        settings = general_settings(self.root)
        return settings.attrs.users_local_management_enabled == 'True'

    def __call__(self):
        self.attrs()
