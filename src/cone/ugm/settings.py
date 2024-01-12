from cone.app.model import Properties
from cone.app.model import SettingsNode
from cone.app.model import XMLProperties
from cone.app.model import node_info
from cone.ugm.localmanager import LocalManagerConfigAttributes
from cone.ugm.utils import general_settings
from node.behaviors import Attributes
from node.utils import instance_property
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
import os


_ = TranslationStringFactory('cone.ugm')


ugm_cfg = Properties()
ugm_cfg.ugm_settings = ''
ugm_cfg.lm_settings = ''

# XXX: move cone.ugm.model.factory_defaults here


class UGMSettings(SettingsNode):
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


@node_info(
    name='ugm_general_settings',
    title=_('ugm_settings_node', default='UGM Settings'),
    description = _(
        'ugm_settings_node_description',
        default='General user and group management settings'
    ),
    icon='ion-person-stalker')
class GeneralSettings(UGMSettings):
    category = _('category_ugm', default='User and Group Management')

    @property
    def config_file(self):
        return ugm_cfg.ugm_settings


@node_info(
    name='ugm_localmanager_settings',
    title=_('localmanager_settings_node', default='Local Manager Settings'),
    description=_(
        'localmanager_settings_node_description',
        default='Local Manager Settings'
    ),
    icon='ion-person')
@plumbing(Attributes)
class LocalManagerSettings(SettingsNode):
    category = _('category_ugm', default='User and Group Management')

    def attributes_factory(self, name=None, parent=None):
        return LocalManagerConfigAttributes(ugm_cfg.lm_settings)

    @property
    def enabled(self):
        settings = general_settings(self.root)
        return settings.attrs.users_local_management_enabled == 'True'

    def __call__(self):
        self.attrs()
