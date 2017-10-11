.. module:: score.pyfilesystem
.. role:: confkey
.. role:: confdefault

******************
score.pyfilesystem
******************

This module provides configurable file systems for your project using
PyFilesystem2_.

.. _PyFilesystem2: https://pyfilesystem2.readthedocs.io


Quickstart
==========

Add *score.pyfilesystem* to the modules list and define your file systems like
this:

.. code-block:: ini
    :emphasize-lines: 4,6-8

    [score.init]
    modules =
        score.ctx
        score.pyfilesystem

    [pyfilesystem]
    path.memory = mem://
    path.tmp = mem://?scope=ctx

You can access the file system called *memory* as a member of the configured
module, or using dict-like access:

>>> type(score.pyfilesystem.memory)
fs.memoryfs.MemoryFS
>>> score.pyfilesystem.memory is score.pyfilesystem['memory']
True

The other filesystem called *tmp* is only accessible through existing context
objects. and will be destroyed along with the context object itself:

>>> with score.ctx.Context() as ctx:
...     ctx.fs.tmp.open('foo.txt').write('bar')


Configuration
=============

.. autofunction:: score.pyfilesystem.init


Details
=======

.. _pyfilesystem_scope:

Filesystem scope
----------------

There are two different modes for filesystems: They are either bound to the
:class:`.ConfiguredPyfilesystemModule` , or they are bound to a
:class:`score.ctx.Context`.

In both cases, registered filesystems will only be created on demand, i.e. when
they are first accessed. They will remain attached to their scope object until
the garbage collector cleans everything up.


API
===

Configuration
-------------

.. autofunction:: score.pyfilesystem.init

.. class:: score.pyfilesystem.Scope

    An :class:`enumeration <enum.Enum>` of valid scope values for registered paths.

    .. attribute:: GLOBAL = "global"
        
        Global scope: the file system can be accessed at any time.

    .. attribute:: CTX = "ctx"

        Context scope: the file system can only be accessed on context objects.

    .. attribute:: CONTEXT = "ctx"

        Alias for the *CTX* value, above

.. class:: score.pyfilesystem.Path

    A :class:`namedtuple` with the attributes *name*, *url* and *scope*. It
    stores the information about a single path registered via
    :meth:`score.pyfilesystem.ConfiguredPyfilesystemModule.register_path`.
    
.. autoclass:: score.pyfilesystem.ConfiguredPyfilesystemModule

    .. attribute:: paths

        A list of :class:`.Path` instances containing all registered paths.

    .. automethod:: score.pyfilesystem.ConfiguredPyfilesystemModule.register_path
