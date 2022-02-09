# Encoding: utf-8
# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
from nagare.services import plugin


class Template(plugin.Plugin):
    DESC = 'Demonstration of a REST application'
    LOAD_PRIORITY = 100
    names = ('rest-default',)

    @staticmethod
    def get_location():
        here = os.path.dirname(__file__)
        name = __name__.split('.')[-1]

        return os.path.join(here, name)
