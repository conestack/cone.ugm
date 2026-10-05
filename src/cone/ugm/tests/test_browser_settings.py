from cone.app import get_root
from cone.tile import render_tile
from cone.tile.tests import TileTestCase
from cone.ugm import testing
from cone.ugm.browser.settings import GeneralSettingsForm
from cone.ugm.browser.settings import group_id_vocab
from cone.ugm.browser.settings import LocalManagerSettingsForm
from cone.ugm.settings import ugm_cfg
from node.utils import UNSET
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import render_view_to_response
from types import SimpleNamespace
from yafowil.base import ExtractionError
import os
import re
import shutil


class BrowserSettingsTests:
    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    @testing.custom_config_path
    @testing.temp_directory
    def test_GeneralSettingsForm(self, tempdir):
        config_file = os.path.join(tempdir, 'ugm.xml')
        ugm_cfg.ugm_settings = config_file
        with open(config_file, 'w') as f:
            f.write('<properties></properties>')

        model = get_root()['settings']['ugm_general']
        request = self.layer.new_request()

        tile = GeneralSettingsForm()
        tile.model = model
        tile.request = request
        with self.layer.authenticated('manager'):
            tile.prepare()

        form = tile.form
        self.assertEqual(
            form.keys(),
            [
                'users_settings',
                'groups_settings',
                'roles_settings',
                'save',
                'came_from',
            ],
        )
        # Each section is a card: the heading its header, the fields its body
        for section in ('users', 'groups', 'roles'):
            self.assertEqual(
                form[f'{section}_settings'].keys(),
                [f'{section}_heading', f'{section}_body'],
            )
        self.assertEqual(
            form['users_settings']['users_body'].keys(),
            [
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
            ],
        )
        self.assertEqual(
            form['groups_settings']['groups_body'].keys(),
            [
                'groups_form_attrmap',
                'groups_listing_columns',
                'groups_listing_default_column',
            ],
        )
        self.assertEqual(
            form['roles_settings']['roles_body'].keys(),
            ['roles_principal_roles_enabled'],
        )

        # The body is structural: the fields keep their path below the form,
        # which is what ``save`` fetches them by
        field = form['roles_settings']['roles_body']['roles_principal_roles_enabled']
        self.assertEqual(field.dottedpath, 'ugm_settings.roles_principal_roles_enabled')

    @testing.principals(
        users={
            'editor': {},
            'manager': {},
        },
        roles={'editor': ['editor'], 'manager': ['manager']},
    )
    def test_general_settings_tiles(self):
        root = get_root()
        general_settings = root['settings']['ugm_general']
        request = self.layer.new_request()

        # Unauthenticated content tile raises error
        self.expectError(
            HTTPForbidden, render_tile, general_settings, request, 'content'
        )

        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden, render_tile, general_settings, request, 'editform'
            )

        # Authenticate and render tile
        with self.layer.authenticated('manager'):
            res = render_tile(general_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm_general/edit"'
        self.assertTrue(res.find(expected) > -1)

        # Three cards, each with its heading as header above its fields
        self.assertEqual(res.count('<fieldset class="card mb-3"'), 3)
        self.assertEqual(res.count('<h5 class="card-header" id="tag-ugm_settings-'), 3)
        self.assertEqual(res.count('<div class="card-body px-0">'), 3)
        self.assertFalse(res.find('<h3') > -1)
        header = res.find('<h5 class="card-header"')
        body = res.find('<div class="card-body px-0">')
        field = res.find('name="ugm_settings.users_account_expiration"')
        self.assertTrue(header < body < field)

    @testing.principals(
        users={
            'editor': {},
            'manager': {},
        },
        roles={'editor': ['editor'], 'manager': ['manager']},
    )
    def test_localmanager_settings_tiles(self):
        root = get_root()
        lm_settings = root['settings']['ugm_localmanager']
        request = self.layer.new_request()

        # Unauthenticated content tile raises error
        self.expectError(HTTPForbidden, render_tile, lm_settings, request, 'content')

        # Form tile raise if not manager
        with self.layer.authenticated('editor'):
            self.expectError(
                HTTPForbidden, render_tile, lm_settings, request, 'editform'
            )

        # Disabled: the card says so instead of showing the form
        with self.layer.authenticated('manager'):
            res = render_tile(lm_settings, request, 'editform')
        self.assertTrue(res.find('<h5 class="card-header">') > -1)
        self.assertTrue(res.find('class="alert alert-warning mb-0"') > -1)
        self.assertFalse(res.find('<form') > -1)

        # Authenticate and render tile
        general_settings = root['settings']['ugm_general']
        general_settings.attrs.users_local_management_enabled = 'True'
        with self.layer.authenticated('manager'):
            res = render_tile(lm_settings, request, 'editform')
        expected = 'form action="http://example.com/settings/ugm_localmanager/edit"'
        self.assertTrue(res.find(expected) > -1)
        # The heading is the header of the settings card, the form its body
        self.assertTrue(
            res.find('<h5 class="card-header">')
            < res.find('class="card-body"')
            < res.find(expected)
        )
        self.assertFalse(res.find('<h1') > -1)
        general_settings.invalidate()

    def _general_form(self):
        tile = GeneralSettingsForm()
        tile.model = get_root()['settings']['ugm_general']
        tile.request = self.layer.new_request()
        return tile

    def test_required_if_users_portrait(self):
        tile = self._general_form()

        def data(extracted, portrait):
            root = {'users_portrait': SimpleNamespace(extracted=portrait)}
            return SimpleNamespace(extracted=extracted, root=root)

        # Not submitted: nothing to check
        self.assertIs(tile.required_if_users_portrait(None, data(UNSET, True)), UNSET)
        # Without portrait support the value may stay empty
        self.assertEqual(tile.required_if_users_portrait(None, data('', False)), '')
        # With portrait support it is required
        self.assertEqual(
            tile.required_if_users_portrait(None, data('portrait', True)), 'portrait'
        )
        err = self.expectError(
            ExtractionError, tile.required_if_users_portrait, None, data('', True)
        )
        self.assertEqual(str(err.msg), 'required_if_users_portrait')

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    @testing.custom_config_path
    @testing.temp_directory
    def test_GeneralSettingsForm_save(self, tempdir):
        # On a copy of the configuration, the shipped one stays as it is
        config_file = os.path.join(tempdir, 'ugm.xml')
        shutil.copy(testing.ugm_config, config_file)
        ugm_cfg.ugm_settings = config_file

        tile = self._general_form()
        attrs = tile.model.attrs
        values = {name: attrs[name] for name in attrs.keys()}
        values['user_id_autoincrement_prefix'] = 'uid-'
        values['groups_listing_default_column'] = 'id'

        class Data:
            def fetch(self, path):
                prefix, name = path.split('.')
                assert prefix == 'ugm_settings'
                return SimpleNamespace(extracted=values[name])

        with self.layer.authenticated('manager'):
            tile.save(None, Data())

        with open(config_file) as f:
            content = f.read()
        self.assertIn(
            '<user_id_autoincrement_prefix>uid-</user_id_autoincrement_prefix>',
            content,
        )
        self.assertIn(
            '<groups_listing_default_column>id</groups_listing_default_column>',
            content,
        )
        # Re read after saving
        self.assertEqual(tile.model.attrs.user_id_autoincrement_prefix, 'uid-')

    def _drop_lm_rules(self):
        # The rules are cached on the settings node (``Attributes``), read
        # from ``ugm_cfg.lm_settings`` on first access. Dropping them makes
        # the next access read the configured file again.
        vars(get_root()['settings']['ugm_localmanager']).pop('__attrs__', None)

    def _lm_form(self):
        tile = LocalManagerSettingsForm()
        tile.model = get_root()['settings']['ugm_localmanager']
        tile.request = self.layer.new_request()
        return tile

    def test_duplicate_rule(self):
        tile = self._lm_form()

        def rule(name, source):
            # The source autocomplete extracts ``{'value': ..., 'label': ...}``
            extracted = {'source': {'value': source, 'label': source.upper()}}
            return SimpleNamespace(name=name, extracted=extracted)

        def data(source, *others):
            current = rule('0', source)
            parent = {each.name: each for each in (current,) + others}
            current.parent = parent
            return current

        # No source yet: nothing to compare
        current = data('', rule('1', ''))
        self.assertIs(tile.duplicate_rule(None, current), current.extracted)
        # Distinct sources
        current = data('a', rule('1', 'b'))
        self.assertIs(tile.duplicate_rule(None, current), current.extracted)
        # A source twice
        current = data('a', rule('1', 'b'), rule('2', 'a'))
        err = self.expectError(ExtractionError, tile.duplicate_rule, None, current)
        self.assertEqual(str(err.msg), 'localmanager_duplicate_rule_error')

    def test_target_not_source(self):
        tile = self._lm_form()

        def data(source, target):
            # gid -> target compound -> targets array -> rule compound
            rule = {'source': SimpleNamespace(extracted={'value': source})}
            targets = SimpleNamespace(parent=rule)
            target_compound = SimpleNamespace(parent=targets)
            return SimpleNamespace(extracted={'value': target}, parent=target_compound)

        self.assertEqual(tile.target_not_source(None, data('a', 'b')), {'value': 'b'})
        err = self.expectError(
            ExtractionError, tile.target_not_source, None, data('a', 'a')
        )
        self.assertEqual(str(err.msg), 'localmanager_target_is_source_error')

    @testing.principals(users={'manager': {}}, roles={'manager': ['manager']})
    @testing.invalidate_settings
    @testing.temp_directory
    def test_LocalManagerSettingsForm_submit(self, tempdir):
        # Through the real form: the autocomplete extracts ``{'value': ...}``,
        # not the bare group id - ``save`` raised ``unhashable type: 'dict'``
        config_file = os.path.join(tempdir, 'localmanager.xml')
        shutil.copy(testing.localmanager_config, config_file)
        lm_settings = ugm_cfg.lm_settings
        ugm_cfg.lm_settings = config_file
        self._drop_lm_rules()
        general_settings = get_root()['settings']['ugm_general']
        general_settings.attrs.users_local_management_enabled = 'True'
        try:
            request = self.layer.new_request()
            # Keyed autocompletes: the hidden field carries the group id, the
            # visible ``.label`` field its title
            rule = 'localmanager_settings.rules.0'
            params = {
                f'{rule}.source': 'admin_group_1',
                f'{rule}.source.label': 'Admin Group 1',
                f'{rule}.targets.0.gid': 'managed_group_3',
                f'{rule}.targets.0.gid.label': 'Managed Group 3',
                f'{rule}.targets.0.default': 'checked',
                f'{rule}.targets.0.default-exists': '1',
                f'{rule}.targets.1.gid': 'managed_group_4',
                f'{rule}.targets.1.gid.label': 'Managed Group 4',
                f'{rule}.targets.1.default-exists': '1',
                'action.localmanager_settings.save': '1',
            }
            request.params.update(params)
            with self.layer.authenticated('manager'):
                render_tile(
                    get_root()['settings']['ugm_localmanager'], request, 'editform'
                )
            attrs = get_root()['settings']['ugm_localmanager'].attrs
            self.assertEqual(sorted(attrs.keys()), ['admin_group_1'])
            self.assertEqual(
                sorted(attrs['admin_group_1']['target']),
                ['managed_group_3', 'managed_group_4'],
            )
            self.assertEqual(attrs['admin_group_1']['default'], ['managed_group_3'])
        finally:
            ugm_cfg.lm_settings = lm_settings
            general_settings.invalidate()
            self._drop_lm_rules()

    @testing.invalidate_settings
    @testing.temp_directory
    def test_LocalManagerSettingsForm_rules_and_save(self, tempdir):
        # On a copy of the rules, the shipped ones stay as they are
        config_file = os.path.join(tempdir, 'localmanager.xml')
        shutil.copy(testing.localmanager_config, config_file)
        lm_settings = ugm_cfg.lm_settings
        ugm_cfg.lm_settings = config_file
        self._drop_lm_rules()
        try:
            tile = self._lm_form()
            # Saving writes where the rules were read from: the copy
            self.assertEqual(tile.model.attrs.file_path, config_file)
            self.assertEqual(
                tile.rules_value,
                [
                    {
                        'source': 'admin_group_1',
                        'targets': [
                            {'gid': 'managed_group_0', 'default': False},
                            {'gid': 'managed_group_1', 'default': True},
                        ],
                    },
                    {
                        'source': 'admin_group_2',
                        'targets': [
                            {'gid': 'managed_group_1', 'default': False},
                            {'gid': 'managed_group_2', 'default': True},
                        ],
                    },
                ],
            )

            # Saving keeps admin_group_1 with new targets, drops admin_group_2
            # and adds admin_group_3
            rules = [
                {
                    'source': 'admin_group_1',
                    'targets': [{'gid': 'managed_group_3', 'default': True}],
                },
                {
                    'source': 'admin_group_3',
                    'targets': [
                        {'gid': 'managed_group_4', 'default': False},
                        {'gid': 'managed_group_5', 'default': True},
                    ],
                },
            ]

            class Data:
                def fetch(self, path):
                    assert path == 'localmanager_settings.rules'
                    return SimpleNamespace(extracted=rules)

            tile.save(None, Data())

            attrs = tile.model.attrs
            self.assertEqual(sorted(attrs.keys()), ['admin_group_1', 'admin_group_3'])
            self.assertEqual(attrs['admin_group_1']['target'], ['managed_group_3'])
            self.assertEqual(attrs['admin_group_1']['default'], ['managed_group_3'])
            self.assertEqual(
                sorted(attrs['admin_group_3']['target']),
                ['managed_group_4', 'managed_group_5'],
            )
            self.assertEqual(attrs['admin_group_3']['default'], ['managed_group_5'])
            with open(config_file) as f:
                content = f.read()
            self.assertIn('<admin_group_3>', content)
            self.assertNotIn('<admin_group_2>', content)
        finally:
            ugm_cfg.lm_settings = lm_settings
            # ``invalidate_settings`` resets the general settings only; the
            # rules read from the copy must not outlive this test
            self._drop_lm_rules()

    @testing.principals(
        users={'manager': {}},
        groups={
            'group_1': {'groupname': 'Group One'},
            'group_2': {'groupname': 'Accounting'},
            'other': {},
        },
        roles={'manager': ['manager']},
    )
    def test_group_id_vocab(self):
        model = get_root()['settings']['ugm_localmanager']
        request = self.layer.new_request()
        # Too short a term searches nothing
        request.params['term'] = 'g'
        self.assertEqual(group_id_vocab(model, request), [])
        # Key and title pairs for the keyed autocomplete, by title. A group
        # without a title shows its id.
        request.params['term'] = 'gr'
        self.assertEqual(
            group_id_vocab(model, request),
            [
                {'id': 'group_2', 'title': 'Accounting'},
                {'id': 'group_1', 'title': 'Group One'},
            ],
        )
        # Found by title as well, case insensitive and anywhere in it
        request.params['term'] = 'ACC'
        self.assertEqual(
            group_id_vocab(model, request), [{'id': 'group_2', 'title': 'Accounting'}]
        )
        request.params['term'] = 'ounti'
        self.assertEqual(
            group_id_vocab(model, request), [{'id': 'group_2', 'title': 'Accounting'}]
        )
        request.params['term'] = 'oth'
        self.assertEqual(
            group_id_vocab(model, request), [{'id': 'other', 'title': 'other'}]
        )

    @testing.principals(
        users={'manager': {}},
        groups={'group_1': {}, 'group_2': {}},
        roles={'manager': ['manager']},
    )
    def test_group_id_vocab_on_local_manager_settings(self):
        # The autocomplete asks the local manager settings node, where the
        # manager holds ``manage``. A relative ``group_id_vocab`` resolved
        # against ``/settings/ugm_localmanager`` hit the settings container,
        # which grants ``view`` only - a 403, and treibstoff redirected to the
        # application root.
        settings = get_root()['settings']

        def call(model):
            request = self.layer.new_request()
            request.accept = 'application/json'
            request.params['term'] = 'gr'
            return render_view_to_response(model, request, name='group_id_vocab')

        with self.layer.authenticated('manager'):
            response = call(settings['ugm_localmanager'])
            self.assertEqual(
                sorted(each['id'] for each in response.json), ['group_1', 'group_2']
            )
            # Not registered anywhere else
            self.assertIsNone(call(settings))

    @testing.principals(
        users={'manager': {}},
        groups={'admin_group_1': {'groupname': 'Admin Group One'}},
        roles={'manager': ['manager']},
    )
    def test_autocomplete_source(self):
        # Source and target fields ask the vocabulary by absolute url
        general_settings = get_root()['settings']['ugm_general']
        general_settings.attrs.users_local_management_enabled = 'True'
        try:
            request = self.layer.new_request()
            with self.layer.authenticated('manager'):
                res = render_tile(
                    get_root()['settings']['ugm_localmanager'], request, 'editform'
                )
        finally:
            general_settings.invalidate()
        # Every source and target field, including the templates of new rows
        sources = re.findall(r"data-source='([^']*)'", res)
        self.assertTrue(sources)
        self.assertEqual(
            set(sources),
            {'http://example.com/settings/ugm_localmanager/group_id_vocab'},
        )
        # Keyed: the id goes in the hidden field, the title is what one sees
        self.assertEqual(set(re.findall(r"data-keys='([^']*)'", res)), {'true'})
        self.assertIn('name="localmanager_settings.rules.0.source.label"', res)
        self.assertIn('value="Admin Group One"', res)


class TestBrowserSettings(TileTestCase, BrowserSettingsTests):
    layer = testing.ugm_layer
