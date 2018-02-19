# Encoding: utf-8

# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import sys

from setuptools import setup, find_packages


if not (2, 7) <= sys.version_info[:2] < (3, 0):
    print 'Python version must be 2.7'
    sys.exit(-2)


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as version:
    LONG_DESCRIPTION = version.read()


setup(
    name='nagare-server',
    author='Net-ng',
    author_email='alain.poirier@net-ng.com',
    description='Nagare Application Server',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    keywords='',
    url='https://github.com/nagareproject/server',
    packages=find_packages(),
    zip_safe=False,
    setup_requires=['setuptools_scm', 'pytest-runner'],
    use_scm_version=True,
    install_requires=['nagare-commands', 'nagare-services', 'nagare-services-logging'],
    tests_require=['pytest'],
    entry_points='''
    [console_scripts]
    nagare-admin = nagare.admin.command:run

    [nagare.commands]
    info = nagare.admin.info:Info
    app = nagare.commands:Commands

    [nagare.commands.app]
    info = nagare.admin.app_info:Info
    serve = nagare.admin.app_serve:Serve

    [nagare.services]
    local = nagare.local:Local
    exceptions = nagare.services.base_exceptions_handler:Handler
    publisher = nagare.server.publishers:Publishers
    application = nagare.server.applications:Application
    '''
)
