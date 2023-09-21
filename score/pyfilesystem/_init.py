# Copyright © 2017,2018 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

from collections import namedtuple
import enum
from fs import open_fs
import keyword
from score.init import extract_conf, ConfiguredModule, InitializationError
import urllib.parse


defaults = {
    'ctx.member': 'fs',
}


def init(confdict, ctx=None):
    """
    Initializes this module acoording to the :ref:`SCORE module initialization
    guidelines <module_initialization>` with the following configuration keys:

    :confkey:`ctx.member.url` :confdefault:`fs`
        The name of the :term:`context member`, that should be registered with
        the configured :mod:`score.ctx` module (if there is one). The default
        value allows you to always access configured file systems within a
        :class:`score.ctx.Context` like the following:

        >>> ctx.fs['my_configured_fs']

    :confkey:`path.*`
        Configuration keys like `path.foo` are file system definitions that must
        contain a valid :ref:`pyfilesystem URL <pyfilesystem:fs-urls>`. These
        values automatically :meth:`register
        <ConfiguredPyfilesystemModule.register_path>` paths during
        initialization. The following example is for registering a memory file
        system called `foo`:

        .. code-block:: ini

            path.foo = mem://

        The only customization is a *scope* parameter, which can also define the
        :term:`scope <pyfilesystem scope>` of a file system. Valid values for
        this parameter are ``global`` (the default) and ``ctx``. The same
        filesystem as above with a scope bound to a context would look like
        this:

        .. code-block:: ini

            path.foo = mem://?scope=ctx

    """
    conf = defaults.copy()
    conf.update(confdict)
    fsconf = ConfiguredPyfilesystemModule()
    for name, url in extract_conf(conf, 'path.').items():
        scope = 'global'
        if '://' in url:
            url = urllib.parse.urlsplit(url)
            query = []
            for key, value in urllib.parse.parse_qsl(url.query):
                if key == 'scope':
                    scope = Scope(value)
                else:
                    query.append((key, value))
            url = [*url]
            url[3] = urllib.parse.urlencode(query)
            url = urllib.parse.urlunsplit(url)
            if '://' not in url:
                # the URL probably does not contain a netloc part and urlunsplit
                # generates something like 'mem:', which is actually valid.
                # pyfilesystem, on the other hand, interprets this as a path on
                # the local filesystem and tries to open it with OSFS.
                # the fix is simple: append two slashes to the first colon
                url = url.replace(':', '://', 1)
        if scope == Scope.CONTEXT and not ctx:
            import score.pyfilesystem
            raise InitializationError(
                score.pyfilesystem,
                'Cannot register object with scope=ctx '
                'without a configured ctx module')
        try:
            fsconf.register_path(name, url, scope=scope)
        except Exception as e:
            import score.pyfilesystem
            raise InitializationError(score.pyfilesystem, str(e)) from e
    if ctx and conf['ctx.member'].lower() != 'none':
        ctx.register(conf['ctx.member'], fsconf._ctx_constructor)
    return fsconf


Path = namedtuple('Path', ('name', 'url', 'scope'))


class Scope(enum.Enum):
    """
    Valid scope values for registered paths.
    """
    GLOBAL = 'global'
    CONTEXT = 'ctx'
    CTX = 'ctx'


class ConfiguredPyfilesystemModule(ConfiguredModule):
    """
    This module's :class:`configuration class <score.init.ConfiguredModule>`.

    You can access all registered file systems either as attributes of this
    class, or using dict access:

    >>> assert score.fs.foo is score.fs['foo']
    """

    def __init__(self):
        import score.pyfilesystem
        super().__init__(score.pyfilesystem)
        self.paths = {}

    def register_path(self, name, url, scope='global'):
        """
        Register a path with given *name* on this instance before the module is
        :ref:`finalized <finalization>`. The *url* must be a valid
        :ref:`pyfilesystem URL <pyfilesystem:fs-urls>`.

        Valid values for *scope* are :class:`.Scope` instances, or their str
        equivalents (``global`` or ``ctx``).
        """
        if self._finalized:
            raise Exception(
                "Cannot register further paths: Module already finalized")
        if name == 'paths':
            raise ValueError('Path name must not be "paths"')
        if name[0] == '_':
            raise ValueError('Path name must not start with an underscore')
        if keyword.iskeyword(name):
            raise ValueError('Path name must not be a python keyword')
        if isinstance(scope, str):
            scope = Scope(scope)
        self.paths[name] = Path(name, url, scope)

    def _ctx_constructor(self, ctx):
        return ContextProxy(self)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            pass
        raise AttributeError(name)

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise TypeError('Key must be string, received %s' % (str(name),))
        if name not in self.paths:
            raise KeyError(name)
        path = self.paths[name]
        if path.scope != Scope.GLOBAL:
            raise KeyError(name)
        value = open_fs(path.url)
        setattr(self, name, value)
        return value

    def __iter__(self):
        return iter(self.paths)

    def __contains__(self, name):
        return name in self.paths


class ContextProxy:
    """
    A proxy object used for accessing file systems on a
    :class:`context object <score.ctx.Context>`.
    """

    def __init__(self, conf):
        self._conf = conf

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            pass
        raise AttributeError(name)

    def __getitem__(self, name):
        if not isinstance(name, str):
            raise TypeError('Key must be string, received %s' % (str(name),))
        if name not in self._conf.paths:
            raise KeyError(name)
        path = self._conf.paths[name]
        if path.scope == Scope.GLOBAL:
            return getattr(self._conf, name)
        value = open_fs(path.url)
        setattr(self, name, value)
        return value
