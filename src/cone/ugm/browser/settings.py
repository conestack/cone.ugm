from cone.app.browser.form import Form
from cone.app.browser.form import YAMLForm
from cone.app.browser.settings import settings_form
from cone.app.browser.settings import SettingsForm
from cone.app.browser.utils import make_url
from cone.app.ugm import ugm_backend
from cone.ugm.settings import GeneralSettings
from cone.ugm.settings import LocalManagerSettings
from node.utils import UNSET
from plumber import plumbing
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from yafowil.base import ExtractionError
from yafowil.widget.autocomplete.widget import unwrap_extracted


_ = TranslationStringFactory('cone.ugm')


@settings_form(interface=GeneralSettings)
@plumbing(SettingsForm, YAMLForm)
class GeneralSettingsForm(Form):
    action_resource = 'edit'
    form_template = 'cone.ugm.browser:forms/general_settings.yaml'

    @property
    def message_factory(self):
        return _

    def required_if_users_portrait(self, widget, data):
        extracted = data.extracted
        if extracted is UNSET:
            return extracted
        if data.root['users_portrait'].extracted and not extracted:
            raise ExtractionError(
                _(
                    'required_if_users_portrait',
                    default='Value is required if portrit support is enabled',
                )
            )
        return extracted

    def save(self, widget, data):
        # XXX: user data.write(model)
        model = self.model
        for attr_name in [
            'users_account_expiration',
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
            'roles_principal_roles_enabled',
        ]:
            val = data.fetch('ugm_settings.%s' % attr_name).extracted
            setattr(model.attrs, attr_name, val)
        model()
        model.invalidate()
        ugm_backend.initialize()


@settings_form(
    interface=LocalManagerSettings,
    path='cone.ugm.browser:templates/localmanager_settings.pt',
)
@plumbing(SettingsForm, YAMLForm)
class LocalManagerSettingsForm(Form):
    action_resource = 'edit'
    form_template = 'cone.ugm.browser:forms/localmanager_settings.yaml'

    @property
    def message_factory(self):
        return _

    @property
    def group_id_vocab_url(self):
        """Source of the group id autocompletes, see ``group_id_vocab``."""
        return make_url(self.request, node=self.model, resource='group_id_vocab')

    def group_title(self, gid):
        """Title a stored group id is shown with - the ``lookup`` of the
        autocompletes, for rules rendered from the configuration."""
        group = self.model.root['groups'].backend.get(gid)
        if group is None:
            return gid
        return group.attrs.get(ugm_backend.group_display_attr) or gid

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
                rule['targets'].append({'gid': gid, 'default': gid in defs['default']})
            rules.append(rule)
        return rules

    def duplicate_rule(self, widget, data):
        """Check for duplicate rules.

        Source and target are autocompletes, which extract ``{'value': ...}``
        rather than the group id - unwrapped here and in ``target_not_source``
        and ``save``.
        """
        source = unwrap_extracted(data.extracted['source'])
        if not source:
            return data.extracted
        exists = [source]
        for val in data.parent.values():
            if val.name == data.name:
                continue
            other = unwrap_extracted(val.extracted['source'])
            if other in exists:
                raise ExtractionError(
                    _(
                        'localmanager_duplicate_rule_error',
                        default='Duplicate access rule',
                    )
                )
            exists.append(other)
        return data.extracted

    def target_not_source(self, widget, data):
        """Check whether source and target are same."""
        source = unwrap_extracted(data.parent.parent.parent['source'].extracted)
        if source == unwrap_extracted(data.extracted):
            raise ExtractionError(
                _(
                    'localmanager_target_is_source_error',
                    default='Target GID equates source GID',
                )
            )
        return data.extracted

    def save(self, widget, data):
        """save rules."""
        attrs = self.model.attrs
        recent = attrs.keys()
        extracted = data.fetch('localmanager_settings.rules').extracted
        for entry in extracted:
            source = unwrap_extracted(entry['source'])
            if source in recent:
                recent.remove(source)
            targets = set()
            defaults = set()
            for target in entry['targets']:
                gid = unwrap_extracted(target['gid'])
                targets.add(gid)
                if target['default']:
                    defaults.add(gid)
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
    context=LocalManagerSettings,
    accept='application/json',
    renderer='json',
    permission='manage',
)
def group_id_vocab(model, request):
    """Groups for the keyed autocomplete of the local manager rules.

    ``[{'id': ..., 'title': ...}]`` - the id is what the rules store, the
    title (``ugm_backend.group_display_attr``) what one picks by; a group
    without one shows its id. Matched by either, case insensitive and
    anywhere in it, sorted by title. Filtered here rather than by the backend
    search, whose matching differs per backend - the file backend compares
    case sensitive, and "acc" would not find "Accounting".

    On the local manager settings node, where the manager holds ``manage``;
    the form passes its absolute url (``group_id_vocab_url``). Asked relative
    to the browser url it hit the settings container, which grants ``view``
    only.
    """
    term = request.params['term']
    if len(term) < 2:
        return []
    attr = ugm_backend.group_display_attr
    term = term.lower()
    groups = []
    for gid, attrs in model.root['groups'].backend.search(attrlist=[attr]):
        title = attrs.get(attr) or gid
        if term in gid.lower() or term in title.lower():
            groups.append({'id': gid, 'title': title})
    return sorted(groups, key=lambda group: group['title'].lower())
