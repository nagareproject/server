# Encoding: utf-8

# --
# Copyright (c) 2008-2021 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as description:
    LONG_DESCRIPTION = description.read()


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
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    install_requires=[
        'nagare-config',
        'nagare-services',
        'nagare-commands-base',
        'nagare-services-logging'
    ],
    entry_points='''
    [nagare.commands]
    app = nagare.admin.command:AppCommands
    spec = nagare.admin.app_spec:Spec2

    [nagare.commands.app]
    info = nagare.admin.app_info:Info
    config = nagare.admin.app_config:Config
    serve = nagare.admin.app_serve:Serve
    spec = nagare.admin.app_spec:Spec

    [nagare.templates]
    default = nagare.templates.default_rest:Template

    [nagare.services]
    local = nagare.local:Local
    exceptions = nagare.services.base_exceptions_handler:ExceptionsService
    publisher = nagare.server.publishers:Publishers
    application = nagare.server.applications:Application
    '''
)
