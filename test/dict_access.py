import fs
import pytest
from score.init import init


def test_access():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.foo': 'mem://',
        }
    })
    assert 'foo' in score.pyfilesystem
    assert isinstance(score.pyfilesystem['foo'], fs.memoryfs.MemoryFS)


def test_equality():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.foo': 'mem://',
        }
    })
    assert score.pyfilesystem['foo'] is score.pyfilesystem.foo


def test_modification_error():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.foo': 'mem://',
        }
    })
    with pytest.raises(TypeError):
        del score.pyfilesystem['foo']
