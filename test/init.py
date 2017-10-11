import fs
import os
import pytest
from score.init import init, InitializationError
from score.pyfilesystem import ConfiguredPyfilesystemModule


def test_blank_start():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
    })
    assert hasattr(score, 'pyfilesystem')
    assert isinstance(score.pyfilesystem, ConfiguredPyfilesystemModule)


def test_simple_url():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.foo': 'mem://',
        }
    })
    assert hasattr(score.pyfilesystem, 'foo')
    assert isinstance(score.pyfilesystem.foo, fs.memoryfs.MemoryFS)


def test_local_path():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.foo': os.path.dirname(__file__),
        }
    })
    assert hasattr(score.pyfilesystem, 'foo')
    assert isinstance(score.pyfilesystem.foo, fs.osfs.OSFS)
    assert score.pyfilesystem.foo.isfile(os.path.basename(__file__))


def test_invalid_name_1():
    init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.path': os.path.dirname(__file__),
        }
    })
    # same init, but name starts with is 'paths' this time
    with pytest.raises(InitializationError):
        init({
            'score.init': {
                'modules': ['score.pyfilesystem'],
            },
            'pyfilesystem': {
                'path.paths': os.path.dirname(__file__),
            }
        })


def test_invalid_name_2():
    init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.path': os.path.dirname(__file__),
        }
    })
    # same init, but name starts with an underscore this time
    with pytest.raises(InitializationError):
        init({
            'score.init': {
                'modules': ['score.pyfilesystem'],
            },
            'pyfilesystem': {
                'path._path': os.path.dirname(__file__),
            }
        })


def test_invalid_scope_1():
    init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.path': 'mem://',
        }
    })
    # same init, but scope is ctx this time
    with pytest.raises(InitializationError):
        init({
            'score.init': {
                'modules': ['score.pyfilesystem'],
            },
            'pyfilesystem': {
                'path.path': 'mem://?scope=ctx',
            }
        })


def test_invalid_scope_2():
    with pytest.raises(InitializationError):
        init({
            'score.init': {
                'modules': ['score.pyfilesystem'],
            },
            'pyfilesystem': {
                'path.path': 'mem://?scope=ctx',
            }
        })
    # same init, but initialize score.ctx this time
    init({
        'score.init': {
            'modules': [
                'score.pyfilesystem',
                'score.ctx',
            ],
        },
        'pyfilesystem': {
            'path.path': 'mem://?scope=ctx',
        }
    })
