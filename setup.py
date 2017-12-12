from setuptools import find_packages
from setuptools import setup
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '1.0a1'
shortdesc = 'User and group management'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


setup(
    name='cone.ugm',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
    ],
    keywords='',
    author='BlueDynamics Alliance',
    author_email='dev@bluedynamics.com',
    url=u'http://github.com/bluedynamics/cone.ugm',
    license='LGPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'cone.app[lxml]',
        'yafowil.widget.array',
        'yafowil.widget.autocomplete',
        'yafowil.widget.datetime',
        'yafowil.widget.dict',
        'yafowil.widget.image',
        'yafowil.yaml',
        'node.ext.ldap'
    ],
    extras_require = dict(
        test=[
            'cone.app[test]',
        ]
    ),
    test_suite='cone.ugm.tests.test_suite'
)
