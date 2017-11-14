# Encoding: utf-8

# --
# (C)opyright Net-ng 2008-2017
#
# This is a Net-ng proprietary source code.
# Any reproduction modification or use without prior written
# approval from Net-ng is strictly forbidden.
# --

import os
import sys

from setuptools import setup, find_packages


if sys.version_info < (2, 7, 0):
    print 'The Python version must be 2.7'
    sys.exit(-2)


with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version:
    VERSION = version.readline().rstrip()


setup(
    name='nagare-server',
    version=VERSION,
    author='Net-ng',
    author_email='alain.poirier@net-ng.com',
    description='Nagare Application Server',
    license='proprietary',
    keywords='',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=('configobj', 'WebOb', 'gevent', 'nagare-services'),
    extras_require={
        'test': ('pytest',),
        'full': (
            'pytest',
        )
    },
    namespace_packages=('nagare', 'nagare.server'),
    setup_requires=('pytest-runner',),
    tests_require=('pytest')
)
