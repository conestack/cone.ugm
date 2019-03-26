
Changes
=======

1.0a1 (unreleased)
------------------

- Use ``cone.tile.tile`` decorator instead of ``cone.tile.registerTile``.
  [rnix]

- Use ``request.has_permission`` instead of ``pyramid.security.has_permission``.
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
