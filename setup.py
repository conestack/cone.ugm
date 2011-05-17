from setuptools import setup, find_packages
import sys, os

version = '0.9before_plugging_merge'
shortdesc = 'cone.ugm'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(name='cone.ugm',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://github.com/bluedynamics/cone.ugm',
      license='GNU General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['cone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'cone.app',
          'node.ext.ldap',
      ],
      extras_require = dict(
          test=[
                'interlude',
          ]
      ),
      tests_require=[
          'interlude',
      ],
      test_suite = "cone.ugm.tests.test_suite",
      entry_points = """\
      [paste.app_factory]
      main = cone.ugm.run:main
      """
      )
