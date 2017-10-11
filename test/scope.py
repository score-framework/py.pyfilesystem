import fs
from score.init import init
import pytest


def test_global_scope():
    score = init({
        'score.init': {
            'modules': ['score.pyfilesystem'],
        },
        'pyfilesystem': {
            'path.mem': 'mem://',
        }
    })
    with score.pyfilesystem.mem.open('foo.txt', 'w') as f:
        f.write('test')
    with score.pyfilesystem.mem.open('foo.txt') as f:
        assert f.read() == 'test'


def test_scope_mismatch():
    score = init({
        'score.init': {
            'modules': [
                'score.ctx',
                'score.pyfilesystem',
            ],
        },
        'pyfilesystem': {
            'path.mem': 'mem://?scope=ctx',
        }
    })
    with pytest.raises(AttributeError):
        score.pyfilesystem.mem


def test_scoped_ctx_members():
    score = init({
        'score.init': {
            'modules': [
                'score.ctx',
                'score.pyfilesystem',
            ],
        },
        'pyfilesystem': {
            'path.mem': 'mem://?scope=ctx',
        }
    })
    with score.ctx.Context() as ctx:
        assert hasattr(ctx, 'fs')
        assert hasattr(ctx.fs, 'mem')
        assert isinstance(ctx.fs.mem, fs.memoryfs.MemoryFS)


def test_global_ctx_members():
    score = init({
        'score.init': {
            'modules': [
                'score.ctx',
                'score.pyfilesystem',
            ],
        },
        'pyfilesystem': {
            'path.mem': 'mem://',
        }
    })
    with score.ctx.Context() as ctx:
        assert hasattr(ctx, 'fs')
        assert hasattr(ctx.fs, 'mem')
        assert isinstance(ctx.fs.mem, fs.memoryfs.MemoryFS)
        assert ctx.fs.mem is score.pyfilesystem.mem


def test_ctx_scope_lifetime():
    score = init({
        'score.init': {
            'modules': [
                'score.ctx',
                'score.pyfilesystem',
            ],
        },
        'pyfilesystem': {
            'path.mem': 'mem://?scope=ctx',
        }
    })
    with score.ctx.Context() as ctx:
        fs1 = ctx.fs.mem
        with fs1.open('foo.txt', 'w') as f:
            f.write('test')
    with score.ctx.Context() as ctx:
        fs2 = ctx.fs.mem
    assert fs1 is not fs2
    with fs1.open('foo.txt') as f:
        assert f.read() == 'test'
    with pytest.raises(fs.errors.ResourceNotFound):
        fs2.open('foo.txt')
