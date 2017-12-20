.. _pyfilesystem_glossary:

.. glossary::

    pyfilesystem scope
        The scope of the created file system object. This is mostly relevant
        for file system implementations that need to perform some operations on
        startup/teardown. If a memory file system's scope is limited to the
        current :class:`score.ctx.Context`, for example, its contents are only
        available within that context.

        See :ref:`pyfilesystem_scope` for details.
