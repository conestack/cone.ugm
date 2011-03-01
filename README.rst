cone.ugm
========

Manage Users and Groups in LDAP via Web Interface.


Getting started
===============

Installation
------------

Clone UGM repository::

    $ git clone git://github.com/bluedynamics/cone.ugm.git

    $ cd cone.ugm

Run bootrsrap and buildout::

    cone.ugm$ python2.6 bootstrap.py -c anon.cfg

    cone.ugm$ ./bin/buildout -c anon.cfg

Start Test Application::

    cone.ugm$ ./bin/testldap start groupOfNames_100_100

    cone.ugm$ ./bin/paster serve ugm.ini


Contributors
============

- Robert Niederreiter <rnix@squarewave.at>

- Florian Friesdorf <flo@chaoflow.net>