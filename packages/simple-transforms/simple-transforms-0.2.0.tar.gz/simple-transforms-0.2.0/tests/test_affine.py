import numpy as np
from flint import flint

import simple_transforms as transform

import pytest

def closeenough(a, b):
    return np.allclose(a, b, atol=1.0e-6)

pytestmark = pytest.mark.parametrize(
    'dtype,compfunc',
    [
        (np.float64,np.allclose),
        (np.float32,closeenough),
        (flint,np.array_equal)
    ]
)

class TestCreation:

    def test_from_mat_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.from_mat()
        with pytest.raises(TypeError):
            a = transform.from_mat(1, 1)
        with pytest.raises(ValueError):
            a = transform.from_mat([1,2,3])
        with pytest.raises(ValueError):
            a = transform.from_mat([[1,2,3],[1,2,3]])
        with pytest.raises(ValueError):
            a = transform.from_mat([[[1,2,3],[1,2,3]]])

    def test_from_mat_4x4(self, dtype, compfunc):
        a = transform.from_mat([[0,1,2,3],[4,5,6,7],[8,9,10,11],[12,13,14,15]], dtype=dtype)
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, np.arange(16).reshape((4,4)))

    def test_from_mat_4x3(self, dtype, compfunc):
        a = transform.from_mat([[0,1,2,3],[4,5,6,7],[8,9,10,11]], dtype=dtype)
        b = np.array([[0,1,2,3],[4,5,6,7],[8,9,10,11],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a,b)

    def test_from_mat_3x3(self, dtype, compfunc):
        a = transform.from_mat([[0,1,2],[3,4,5],[6,7,8]], dtype=dtype)
        b = np.array([[0,1,2,0],[3,4,5,0],[6,7,8,0],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a,b)


class TestTranslation:

    def test_translation_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.trans()
        with pytest.raises(ValueError):
            a = transform.trans(1,2)
        with pytest.raises(ValueError):
            a = transform.trans([1,2])
        with pytest.raises(ValueError):
            a = transform.trans([[1,2,3]])
        with pytest.raises(TypeError):
            a = transform.trans([1,2,3], foo=[4,5,6])

    def test_translation(self, dtype, compfunc):
        a = transform.trans([1,2,3], dtype=dtype)
        b = np.array([[1,0,0,1],[0,1,0,2],[0,0,1,3],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, b)

    def test_translation_with_center(self, dtype, compfunc):
        a = transform.trans([5,6,7], center=[0,1,3], dtype=dtype)
        b = np.array([[1,0,0,5],[0,1,0,6],[0,0,1,7],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, b)


class TestScale:

    def test_scale_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.scale()
        with pytest.raises(ValueError):
            a = transform.scale(1,2)
        with pytest.raises(ValueError):
            a = transform.scale([1])
        with pytest.raises(ValueError):
            a = transform.scale([[1,2,3]])
        with pytest.raises(TypeError):
            a = transform.scale([1,2,3], foo=[4,5,6])

    def test_scale_scalar(self, dtype, compfunc):
        comp = np.eye(4, dtype=np.float64)
        a = transform.scale(2, dtype=dtype)
        for i in range(3):
            comp[i,i] = 2
        assert a.shape == (4,4)
        assert compfunc(a, comp)
        a = transform.scale(0.5, dtype=dtype)
        for i in range(3):
            comp[i,i] = 0.5
        assert a.shape == (4,4)
        assert compfunc(a, comp)
        s = flint(1.0)/3 if dtype == flint else 1/3
        a = transform.scale(s, dtype=flint)
        for i in range(3):
            comp[i,i] = 1/3
        assert a.shape == (4,4)
        assert compfunc(a, comp)

    def test_scale_vec(self, dtype, compfunc):
        comp = np.eye(4, dtype=np.float64)
        a = transform.scale([2,3,4], dtype=dtype)
        comp[0,0] = 2
        comp[1,1] = 3
        comp[2,2] = 4
        assert a.shape == (4,4)
        assert compfunc(a, comp)

    def test_scale_with_center(self, dtype, compfunc):
        comp = np.eye(4, dtype=np.float64)
        a = transform.scale(2, center=[1,2,3], dtype=dtype)
        for i in range(3):
            comp[i,i] = 2
        comp[0,3] = -1
        comp[1,3] = -2
        comp[2,3] = -3
        assert a.shape == (4,4)
        assert compfunc(a, comp)


class TestRotation:

    def test_rotation_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.rot()
        with pytest.raises(TypeError):
            a = transform.rot(1)
        with pytest.raises(ValueError):
            a = transform.rot(1,2,3)
        with pytest.raises(ValueError):
            a = transform.rot(1,1)
        with pytest.raises(ValueError):
            a = transform.rot('xoo',1)
        with pytest.raises(ValueError):
            a = transform.rot([1],1)
        with pytest.raises(TypeError):
            a = transform.rot([1,2,3],1, foo=[0,0,0])

    def test_rot_x(self, dtype, compfunc):
        a = transform.rot('x', np.pi/2, dtype=dtype)
        b = np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, b)

    def test_rot_y(self, dtype, compfunc):
        a = transform.rot('Y', np.pi/2, dtype=dtype)
        b = np.array([[0,0,1,0],[0,1,0,0],[-1,0,0,0],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, b)

    def test_rot_z(self, dtype, compfunc):
        a = transform.rot('z', np.pi/2, dtype=dtype)
        b = np.array([[0,-1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
        assert isinstance(a, np.ndarray)
        assert a.shape == (4,4)
        assert compfunc(a, b)

    def test_rot_aa(self, dtype, compfunc):
        a = transform.rot('x', 1, dtype=dtype)
        b = transform.rot([1,0,0], 1, dtype=dtype)
        assert compfunc(a, b)
        a = transform.rot('y', 1.5, dtype=dtype)
        b = transform.rot([0,2,0], 1.5, dtype=dtype)
        assert compfunc(a, b)
        a = transform.rot('z', 0.5, dtype=dtype)
        b = transform.rot([0,0,0.5], 0.5, dtype=dtype)
        assert compfunc(a, b)

    def test_rot_with_center(self, dtype, compfunc):
        a = transform.rot('z',np.pi/2, center=[1,0,0], dtype=dtype)
        b = np.array([[0,-1,0,1],[1,0,0,-1],[0,0,1,0],[0,0,0,1]], dtype=np.float64)
        assert compfunc(a, b)


class TestRefection:

    def test_refl_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.refl()
        with pytest.raises(ValueError):
            a = transform.refl('xxo')
        with pytest.raises(ValueError):
            a = transform.refl(1)
        with pytest.raises(ValueError):
            a = transform.refl([1,2])
        with pytest.raises(TypeError):
            a = transform.refl([1,2,3], foo=[0,0,0])
        
    def test_refl_xyz(self, dtype, compfunc):
        a = transform.refl('x', dtype=dtype)
        b = np.eye(4)
        b[0,0] = -1
        assert compfunc(a, b)
        a = transform.refl('Y', dtype=dtype)
        b = np.eye(4)
        b[1,1] = -1
        assert compfunc(a, b)
        a = transform.refl('z', dtype=dtype)
        b = np.eye(4)
        b[2,2] = -1
        assert compfunc(a, b)

    def test_refl_u(self, dtype, compfunc):
        a = transform.refl([1,1,1], dtype=dtype)
        bb = 1/np.sqrt(3)
        b = np.eye(4)
        for i in range(3):
            for j in range(3):
                b[i,j] -= 2*bb*bb
        assert compfunc(a, b)

    def test_refl_with_center(self, dtype, compfunc):
        a = transform.refl('x', center=[1,0,0], dtype=dtype)
        b = np.eye(4)
        b[0,0] = -1
        b[0,3] = 2
        assert compfunc(a, b)


class TestSkew:

    def test_skew_exc(self, dtype, compfunc):
        with pytest.raises(TypeError):
            a = transform.skew()
        with pytest.raises(TypeError):
            a = transform.skew('x')
        with pytest.raises(ValueError):
            a = transform.skew([1], [1,2,3])
        with pytest.raises(ValueError):
            a = transform.skew('z', [1,2])
        with pytest.raises(TypeError):
            a = transform.skew('z', [1,2,3], foo=[0,0,0])

    def test_skew_z(self, dtype, compfunc):
        a = transform.skew('z',[2,3,4], dtype=dtype)
        b = np.eye(4)
        b[0,2] = 2
        b[1,2] = 3
        assert compfunc(a, b)

    def test_skew_n(self, dtype, compfunc):
        a = transform.skew('z',[2,3,4], dtype=dtype)
        b = transform.skew([0,0,1],[2,3,1], dtype=dtype)
        c = transform.skew([0,0,3],[2,3,5], dtype=dtype)
        assert compfunc(a, b)
        assert compfunc(a, c)

    def test_skew_with_center(self, dtype, compfunc):
        a = transform.skew('z',[1,0,0],center=[0,0,1], dtype=dtype)
        b = np.eye(4)
        b[0,2] = 1
        b[0,3] = -1
        assert compfunc(a, b)


class TestRescale:

    def test_single(self, dtype, compfunc):
        a = np.array([2,2,2,2], dtype=dtype)
        b = np.empty_like(a)
        transform.rescale(a,b)
        assert compfunc(b, [1,1,1,1])

    def test_multiple(self, dtype, compfunc):
        a = np.array([[2,2,2,2],[3,3,3,3],[4,4,4,4]], dtype=dtype)
        b = np.empty((3,4), dtype=dtype)
        transform.rescale(a,b)
        assert compfunc(b, np.ones((3,4)))

class TestCombine:

    def test_eye(self, dtype, compfunc):
        a = transform.eye(dtype=dtype)
        b = transform.rot('x',np.pi/2, dtype=dtype)
        c = transform.combine(a,b)
        assert compfunc(c, b)
        c = transform.combine(b,a)
        assert compfunc(c, b)

    def test_combine(self, dtype, compfunc):
        a = transform.rot('z', np.pi, dtype=dtype)
        b = transform.combine(a, a)
        assert compfunc(b, np.eye(4))

    def test_reduce(self, dtype, compfunc):
        a = transform.rot('x', 2*np.pi/10)
        b = transform.transform_reduce([a]*10)
        assert np.all( b == np.eye(4) )


class TestApply:

    def test_apply_vertex(self, dtype, compfunc):
        v = [1,0,0]
        r = transform.rot('z',np.pi/2, dtype=dtype)
        vr = transform.apply(r, v)
        assert compfunc(vr, [0,1,0])

    def test_apply_vertices(self, dtype, compfunc):
        v = [[1,0,0],[2,0,0],[3,0,0]]
        vt = [[0,1,0],[0,2,0],[0,3,0]]
        r = transform.rot('z',np.pi/2, dtype=dtype)
        vr = transform.apply(r, v)
        assert compfunc(vr, vt)

    def test_apply_homo(self, dtype, compfunc):
        h = [1,0,0,1]
        r = transform.rot('z',np.pi/2, dtype=dtype)
        hr = transform.apply(r, h)
        assert compfunc(hr, [0,1,0,1])

    def test_apply_homos(self, dtype, compfunc):
        h = [[1,0,0,1], [2,0,0,1], [3,0,0,1], [4,0,0,1]]
        ht = [[0,1,0,1], [0,2,0,1], [0,3,0,1], [0,4,0,1]]
        r = transform.rot('z',np.pi/2, dtype=dtype)
        hr = transform.apply(r, h)
        assert compfunc( hr, ht)
