#!/bin/bash

export LDAP_ADD_BIN=parts/openldap/bin/ldapadd
export LDAP_DELETE_BIN=parts/openldap/bin/ldapdelete
export SLAPD_BIN=parts/openldap/libexec/slapd
export SLAPD_URIS=ldap://127.0.0.1:12345
export ADDITIONAL_LDIF_LAYERS=

./bin/py -m cone.ugm.tests.__init__

unset LDAP_ADD_BIN
unset LDAP_DELETE_BIN
unset SLAPD_BIN
unset SLAPD_URIS
unset ADDITIONAL_LDIF_LAYERS
