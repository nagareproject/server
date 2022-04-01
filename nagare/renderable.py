# --
# Copyright (c) 2008-2022 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare import presentation
from nagare.renderers import xml


class Renderable(xml.Renderable):

    def __init__(self, o=None, view=presentation.ANON_VIEW):
        """Initialisation

        In:
          - ``o`` -- the python object (or renderable) to transform into a renderable
          - ``view`` -- the name of the view to use (``None`` for the default view)
        """
        self.o = o
        self.view = view

    def __call__(self):
        """Return the inner object
        """
        return self.o

    def render(self, renderer, view=presentation.CURRENT_VIEW, *args, **kw):
        """Rendering method of a renderable object

        Forward to the ``presentation`` service
        """
        return presentation.render(self.o, renderer, self, self.view, view, *args, **kw)

    def __bool__(self):
        return bool(self.o)
    __nonzero__ = __bool__

    def __repr__(self):
        return '<%s with %s at 0x%x on object %r>' % (
            self.__class__.__name__.lower(),
            "view '%s'" % self.view if self.view else 'default view',
            id(self),
            self.o
        )
