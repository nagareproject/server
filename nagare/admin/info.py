# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import sys

import pkg_resources

from nagare.admin import command


class Info(command.Command):
    DESC = 'Display various informations'
    WITH_CONFIG_FILENAME = False

    @staticmethod
    def run():
        print sys.subversion[0], sys.version
        print
        print 'Nagare server version', pkg_resources.get_distribution('nagare-server').version
