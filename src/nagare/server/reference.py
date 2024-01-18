# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""Import an object from a string reference.

The possible reference syntaxes are:

  - ``'python <module>:<object>'`` -- loads an object from a Python module
    (for example: ``'python os.path:isfile'``)
  - ``'<module>:<object>'``  -- same as ``'python <module>:<object>'``
  - ``'file <file>:<object>'`` -- loads an object from a file
    (for example: ``'file /tmp/counter.py:Counter'``)
  - ``'egg <dist>:<app>'`` -- loads the registered application ``<app>``
    from the ``<dist>`` distribution
    (for example: ``'egg nagare:admin'`` or ``'egg nagare.examples:wiki'``)
  - ``'app <app>'`` -- load the registered application ``<app>``
    (for example: ``'app examples'``)
"""

import os
import sys
from importlib import metadata

from nagare.packaging import Distribution


def get_file(o):
    module = getattr(o, '__module__', None)
    if module is not None:
        o = sys.modules[module]

    return getattr(o, '__file__', None)


def load_distribution(dist, path=None):
    """Load a distribution.

    In:
      - ``dist`` -- name of the distribution

    Return:
      - the distribution
    """
    dist = metadata.distribution(dist)
    location = Distribution(dist).editable_project_location or str(dist.locate_file(path or ''))

    return dist, location


def load_entry_point(entry_point, entry):
    """Load an object registered under an entry point.

    In:
      - ``app`` -- name of the object
      - ``entry_point`` -- name of the entry_point

    Return:
      - (the object, the distribution of the object)
    """
    all_entry_points = metadata.entry_points()
    entry_points = (
        all_entry_points.get(entry_point, ())
        if isinstance(all_entry_points, dict)
        else all_entry_points.select(group=entry_point)
    )
    entry = {entry.name: entry for entry in entry_points}.get(entry)
    if entry is None:
        return None, None

    o = entry.load()
    return o, get_file(o)


def load_service(service, _=None):
    return load_entry_point('nagare.services', service)


def load_publisher(publisher, _=None):
    return load_entry_point('nagare.publishers', publisher)


def load_app(app, _=None):
    """Load a registered application.

    In:
      - ``app`` -- name of the application
      - ``_`` -- *unused**

    Return:
      - (the application, the distribution of the application)
    """
    return load_entry_point('nagare.applications', app)


def load_module(module, o=None):
    """Load an object from a Python module.

    In:
      - ``module`` -- name of the module
      - ``app`` -- name of the object to load

    Return:
      - (the object, None)
    """
    r = __import__(module, fromlist=('',))

    if o is not None:
        r = getattr(r, o, None)

    return r, get_file(r)


def load_file(filename, app):
    """Load an object from a file.

    In:
      - ``filename`` -- name of the file
      - ``app`` -- name of the object to load

    Return:
      - (the object, None)
    """
    dirname = os.path.abspath(os.path.dirname(filename))
    if dirname not in sys.path:
        sys.path.insert(0, dirname)

    name = os.path.splitext(os.path.basename(filename))[0]
    try:
        return load_module(name, app)
    except (ImportError, ModuleNotFoundError):
        return None, None


loaders = {
    'dist': load_distribution,
    'entry-point': load_entry_point,
    'service': load_service,
    'publisher': load_publisher,
    'app': load_app,
    'python': load_module,
    'file': load_file,
}


def parse_reference(reference, default_scheme=''):
    """Parse a reference.

    In:
      - ``reference`` -- reference as a string

    Return:
      - a tuple (scheme, reference, object loaded, distribution where this object is located or ``None``)
    """
    reference = reference.strip()

    if ' ' in reference:
        scheme, reference = reference.split(maxsplit=1)
    else:
        scheme = default_scheme

    if ':' in reference:
        reference, o = reference.split(':', 1)
    else:
        o = None

    return scheme, reference, o


def is_reference(reference, default_scheme=''):
    return parse_reference(reference, default_scheme)[0] in loaders


def load_object(reference, default_scheme='python'):
    """Load an object from a reference.

    In:
      - ``reference`` -- reference as a string

    Return:
      - a tuple (object loaded, distribution where this object is located or ``None``)
    """
    scheme, reference, o = parse_reference(reference, default_scheme)
    return loaders[scheme](reference, o)
