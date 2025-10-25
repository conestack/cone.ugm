from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test
import os


def read_file(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()


version = '1.0.dev0'
shortdesc = 'User and group management'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


class Test(test):

    def run_tests(self):
        from cone.ugm import tests
        tests.run_tests()


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
    author='Cone Contributors',
    author_email='dev@conestack.org',
    url='http://github.com/conestack/cone.ugm',
    license='LGPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'natsort',
        'Pillow<10.0.0',
        'cone.app[lxml]>=1.0.3,<1.1.0',
        'yafowil.widget.array<2.0.0',
        'yafowil.widget.autocomplete<2.0.0',
        'yafowil.widget.datetime<2.0.0',
        'yafowil.widget.dict<2.0.0',
        'yafowil.widget.image<2.0.0',
        'yafowil.yaml<3.0.0'
    ],
    extras_require=dict(
        test=[
            'zope.testrunner'
        ]
    ),
    tests_require=[
        'zope.testrunner'
    ],
    cmdclass=dict(test=Test)
)
