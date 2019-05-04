TODO
====

- improve login form field factory to hook up login extractor to related
  login name form field widget.

- merge code from model/*.py in model.py.

- complete test coverage.

- generalize and copy tests relevant for LDAP ugm backend testing to cone.ldap

- use file ugm backend for cone.ugm test layer.

- document principal form field customization.

- move LDAP related code to ``cone.ldap``.
    - move object class handling from user form to node.ext.ldap
    - check roles support in browser roles via UGM API instead of LDAP
      settings
