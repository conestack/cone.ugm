from cone.app.browser.form import Form
from cone.app.browser.form import YAMLForm
from cone.app.browser.layout import ProtectedContentTile
from cone.app.browser.settings import SettingsBehavior
from cone.app.ugm import ugm_backend
from cone.tile import tile
from cone.ugm.settings import GeneralSettings
from cone.ugm.settings import LocalManagerSettings
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from yafowil.base import ExtractionError
from yafowil.base import UNSET


_ = TranslationStringFactory('cone.ugm')


@tile(
    name='content',
    path='templates/general_settings.pt',
    interface=GeneralSettings,
    permission='manage')
class GeneralSettingsContent(ProtectedContentTile):
    pass


@tile(name='editform', interface=GeneralSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class GeneralSettingsForm(Form):
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/general_settings.yaml'

    @property
    def message_factory(self):
        return _

    def required_if_users_account_expiration(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        if data.root['users_account_expiration'].extracted and not extracted:
            raise ExtractionError(_(
                'required_if_users_account_expiration',
                default='Value is required if account expiration is enabled'
            ))
        return extracted

    def required_if_users_portrait(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        if data.root['users_portrait'].extracted and not extracted:
            raise ExtractionError(_(
                'required_if_users_portrait',
                default='Value is required if portrit support is enabled'
            ))
        return extracted

    def save(self, widget, data):
        # XXX: user data.write(model)
        model = self.model
        for attr_name in [
            'users_account_expiration',
            'users_expires_attr',
            'users_expires_unit',
            'user_id_autoincrement',
            'user_id_autoincrement_prefix',
            'user_id_autoincrement_start',
            'users_portrait',
            'users_portrait_attr',
            'users_portrait_accept',
            'users_portrait_width',
            'users_portrait_height',
            'users_local_management_enabled',
            'users_login_name_attr',
            'users_exposed_attributes',
            'users_form_attrmap',
            'users_listing_columns',
            'users_listing_default_column',
            'groups_form_attrmap',
            'groups_listing_columns',
            'groups_listing_default_column',
            'roles_principal_roles_enabled'
        ]:
            val = data.fetch('ugm_settings.%s' % attr_name).extracted
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
        ugm_backend.initialize()


@tile(
    name='content',
    path='templates/localmanager_settings.pt',
    interface=LocalManagerSettings,
    permission='manage')
class LocalManagerSettingsTile(ProtectedContentTile):
    pass


@tile(name='editform', interface=LocalManagerSettings, permission='manage')
@plumbing(SettingsBehavior, YAMLForm)
class LocalManagerSettingsForm(Form):
    action_resource = u'edit'
    form_template = 'cone.ugm.browser:forms/localmanager_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def rules_value(self):
        """Return value format:

            return [{
                'source': 'aaa',
                'targets': [{
                    'gid': 'bbb',
                    'default': False,
                }]
            }]
        """
        rules = list()
        items = self.model.attrs.items()
        items = sorted(items, key=lambda x: x[0])
        for source, defs in items:
            rule = dict()
            rule['source'] = source
            rule['targets'] = list()
            targets = sorted(defs['target'])
            for gid in targets:
                rule['targets'].append({
                    'gid': gid,
                    'default': gid in defs['default']
                })
            rules.append(rule)
        return rules

    def duplicate_rule(self, widget, data):
        """Check for duplicate rules.
        """
        source = data.extracted['source']
        if not source:
            return data.extracted
        exists = [source]
        for val in data.parent.values():
            if val.name == data.name:
                continue
            other = val.extracted['source']
            if other in exists:
                raise ExtractionError(_(
                    'localmanager_duplicate_rule_error',
                    default='Duplicate access rule'
                ))
            exists.append(other)
        return data.extracted

    def target_not_source(self, widget, data):
        """Check whether source and target are same.
        """
        source = data.parent.parent.parent['source'].extracted
        if source == data.extracted:
            raise ExtractionError(_(
                'localmanager_target_is_source_error',
                default='Target GID equates source GID'
            ))
        return data.extracted

    def save(self, widget, data):
        """save rules.
        """
        attrs = self.model.attrs
        recent = attrs.keys()
        extracted = data.fetch('localmanager_settings.rules').extracted
        for entry in extracted:
            source = entry['source']
            if source in recent:
                recent.remove(source)
            targets = set()
            defaults = set()
            for target in entry['targets']:
                targets.add(target['gid'])
                if target['default']:
                    defaults.add(target['gid'])
            rule = {
                'target': list(targets),
                'default': list(defaults),
            }
            attrs[source] = rule
        for source in recent:
            del attrs[source]
        self.model()


@view_config(
    name='group_id_vocab',
    accept='application/json',
    renderer='json',
    permission='manage')
def group_id_vocab(model, request):
    term = request.params['term']
    if len(term) < 2:
        return []
    backend = model.root['groups'].backend
    return backend.search(criteria={'id': '%s*' % term})
