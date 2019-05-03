TODO
====

- generalize tests
  - generalize and copy tests relevant for LDAP ugm backend testing to cone.ldap
  - use file ugm backend for cone.ugm test layer.

- provide translations for reserved user and group attributes.

- rename reserver id on groups to group_id.

- rename reserved id on users to user_id.

- move LDAP related code to ``cone.ldap``.
    - move object class handling from user form to node.ext.ldap
    - check roles support in browser roles via generic API instead of LDAP
      settings

- make UI work with any kind of ``node.ext.ugm`` based implementations.

- provide application model for ``node.ext.ugm.file`` implementation as default.
