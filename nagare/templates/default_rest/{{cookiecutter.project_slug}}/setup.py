# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from setuptools import setup, find_packages

VERSION = '0.0.1'


setup(
    name='{{cookiecutter.project_slug}}',
    version=VERSION,
    author='',
    author_email='',
    description='',
    license='',
    keywords='',
    url='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=('nagare',),
    entry_points="""
    [nagare.applications]
    {{cookiecutter.project_slug}} = {{cookiecutter.project_slug}}.app:app
    """
)

