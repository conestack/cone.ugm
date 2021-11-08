Changes
=======

1.0a4 (2021-11-08)
------------------

- Adopt import path of ``safe_decode`` and ``node_path``.
  [rnix]


1.0a3 (2021-10-25)
------------------

- Fix ``UsersListing`` and ``GroupsListing`` search filter to ignore
  ``None`` values.

- Increase listing slice size to 15.
  [rnix]

- Add ``change_password`` form.
  [rnix]

- Add support for objects events on user and group add/modify/delete.
  [zworkb]


1.0a2 (2020-11-12)
------------------

- Fix delete principal.
  [rnix]


1.0a1 (2020-07-09)
------------------

- Use ``ContentAddForm`` and ``ContentEditForm`` behaviors instead of B/C
  ``AddBehavior`` and ``EditBehavior`` for user and group form.
  [rnix]

- Use ``layout_config`` decorator introduced in ``cone.app 1.0rc1``.
  [rnix]

- Remove ``cone.ugm.model.users.users_factory`` and
  ``cone.ugm.model.groups.groups_factory``. Register related node classes
  directly as app entries.
  [rnix]

- Bind UGM columns content view to UGM models.
  [rnix]

- Move LDAP related code to ``cone.ldap``.
  [rnix]

- Users autoincrement start setting value may be empty in config.
  [rnix]

- Do not remember users and groups on volatile storage.
  [rnix]

- Use ``IUgm.invalidate`` for invalidation of users and groups on UGM backend.
  [rnix]

- Rename ``cone.ugm.browser.listing.ColumnListing.query_items`` to
  ``listing_items``.
  [rnix]

- Turn ``cone.ugm.browser.group.Users`` and ``cone.ugm.browser.user.Groups``
  property descriptors into ``ColumnListing`` deriving tiles.
  [rnix]

- Remove superfluous ``jQuery.sortElements.js`` and ``naturalSort.js``.
  [rnix]

- Move plugin config code inside main hook function.
  [rnix]

- Python 3 Support.
  [rnix]

- Convert doctests to unittests.
  [rnix]

- Use ``cone.app.ugm.ugm_backend`` instead of ``cone.app.cfg.auth``.
  [rnix]

- Use ``cone.tile.tile`` decorator instead of ``cone.tile.registerTile``.
  [rnix]

- Use ``request.has_permission`` instead of ``pyramid.security.has_permission``.
  [rnix]

- Remove inout widget. Listing widget is the only principal membership now.
  Remove corresponding ``default_membership_assignment_widget``,
  ``user_display_name_attribute`` and ``group_display_name_attribute`` from
  settings
  [rnix]

- Change UI. Principal form and principal membership are not displayed
  in right column together any more. When viewing a principals content, left
  column displays the listing and right column the principal form. When
  viewing a principal, left column displays the principal form and right
  column displays the principal membership.
  [rnix]

- Update to cone.app >= 1.0.
  [rnix]

- Change license to LGPLv3.
  [rnix]


0.9.7
-----

- Directly depend on ``lxml`` in ``setup.py``
  [rnix, 2014-05-13]


0.9.6
-----

- Adopt dependencies.
  [rnix, 2013-01-10]


0.9.5
-----

- Portrait CSS fix.
  [rnix, 2012-10-30]

- Python 2.7 Support.
  [rnix, 2012-10-16]

- adopt to ``cone.app`` 0.9.4
  [rnix, 2012-07-29]

- adopt to ``node`` 0.9.8
  [rnix, 2012-07-29]

- adopt to ``plumber`` 1.2
  [rnix, 2012-07-29]

- Simplify ``cone.ugm.browser.actions``.
  [rnix, 2012-07-26]

- Add local manager functionality.
  [rnix, 2012-07-25]


0.9.4
-----

- Get rid of BBB classes usage from ``cone.app``.
  [rnix, 2012-05-18]

- Fix invalidation after settings form save.
  [rnix, 2012-04-23]

- Portrait Image support.
  [rnix, 2012-04-21]

- Configuration for attributes exposed to attribute map.
  [rnix, 2012-04-19]

- Invalidate after creating principal or roles container.
  [rnix, 2012-04-19]

- Adopt ``expires`` blueprint to ``yafowil.widget.datetime`` 1.3.
  [rnix, 2012-04-19]


0.9.3
-----

- Add Autoincrement Feature for user ids.
  [rnix, 2012-03-30]


0.9.2
-----

- Account expiration widget improvements.
  [rnix, 2012-03-20]


0.9.1
-----

- Add account expiration functionality.
  [rnix, 2011-03-06]

- Make display field of In-Out widget configurable.
  [rnix, 2011-01-31]

- Dynamic width CSS.
  [rnix, 2011-12-18]

- Get rid of global ``cone.ugm.backend``. ``cone.app.cfg.auth`` is returend
  by ``cone.ugm.model.utils.ugm_backend``.
  [rnix, 2011-11-22]

- Explicit names for settings forms.
  [rnix, 2011-11-18]

- Add node properties for users and groups to get displayed in navtree if
  displayed.
  [rnix, 2011-11-16]


0.9
---

- Initial release.
