# Copyright 2014, 2015 The ODL development group
#
# This file is part of ODL.
#
# ODL is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ODL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ODL.  If not, see <http://www.gnu.org/licenses/>.


# Imports for common Python 2/3 codebase
from __future__ import print_function, division, absolute_import

from future import standard_library
standard_library.install_aliases()

# External module imports
import unittest
import numpy as np

# ODL imports
import odl
from odl import L2
from odl.util.testutils import almost_equal


def func_1d(x):
    return x**2


def func_1d_apply(x, out):
    out[:] = x**2


def func_2d_novec(x):
    return x[0]**2 + x[1]


def func_2d_array(x):
    x0, x1 = x[:, 0], x[:, 1]
    return x0**2 + x1


def func_2d_array_apply(x, out):
    x0, x1 = x[:, 0], x[:, 1]
    out[:] = x0**2
    out += x1


def func_2d_mg(x):
    x0, x1 = x
    return x0**2 + x1


def func_2d_mg_apply(x, out):
    x0, x1 = x
    out[:] = x0**2 + x1


def cfunc_2d_novec(x):
    return x[0]**2 + 1j*x[1]


def cfunc_2d_array(x):
    x0, x1 = x[:, 0], x[:, 1]
    return x0**2 + 1j*x1


def cfunc_2d_array_apply(x, out):
    x0, x1 = x[:, 0], x[:, 1]
    out[:] = x0**2
    out += 1j*x1


def cfunc_2d_mg(x):
    x0, x1 = x
    return x0**2 + 1j*x1


def cfunc_2d_mg_apply(x, out):
    x0, x1 = x
    out[:] = x0**2 + 1j*x1


def other_func_2d_novec(x):
    return -x[0] + abs(x[1])


def other_func_2d_array(x):
    x0, x1 = x[:, 0], x[:, 1]
    return -x0 + abs(x1)


def other_func_2d_array_apply(x, out):
    x0, x1 = x[:, 0], x[:, 1]
    out[:] = abs(x1)
    out -= x0


def other_func_2d_mg(x):
    x0, x1 = x
    return -x0 + abs(x1)


def other_func_2d_mg_apply(x, out):
    x0, x1 = x
    out[:] = -x0 + abs(x1)


def other_cfunc_2d_novec(x):
    return -1j*x[0] + abs(x[1])


def other_cfunc_2d_array(x):
    x0, x1 = x[:, 0], x[:, 1]
    return -1j*x0 + abs(x1)


def other_cfunc_2d_array_apply(x, out):
    x0, x1 = x[:, 0], x[:, 1]
    out[:] = abs(x1)
    out -= 1j*x0


def other_cfunc_2d_mg(x):
    x0, x1 = x
    return -1j*x0 + abs(x1)


def other_cfunc_2d_mg_apply(x, out):
    x0, x1 = x
    out[:] = -1j*x0 + abs(x1)


class L2TestInit(ODLTestCase):

    def init_test(self):
        intv = odl.Interval(0, 1)
        L2(intv)
        L2(intv, field=odl.RealNumbers())
        L2(intv, field=odl.ComplexNumbers())

        rect = odl.Rectangle([0, 0], [1, 2])
        L2(rect)
        L2(rect, field=odl.RealNumbers())
        L2(rect, field=odl.ComplexNumbers())

        cube = odl.Cuboid([0, 0, 0], [1, 2, 3])
        L2(cube)
        L2(cube, field=odl.RealNumbers())
        L2(cube, field=odl.ComplexNumbers())

        ndbox = odl.IntervalProd([0]*10, np.arange(1, 11))
        L2(ndbox)
        L2(ndbox, field=odl.RealNumbers())
        L2(ndbox, field=odl.ComplexNumbers())


class L2TestAttributes(ODLTestCase):

    def simple_attr_test(self):
        intv = odl.Interval(0, 1)
        l2 = L2(intv)
        l2_r = L2(intv, field=odl.RealNumbers())
        l2_c = L2(intv, field=odl.ComplexNumbers())

        self.assertEquals(l2.domain, intv)
        self.assertEquals(l2.range, odl.RealNumbers())
        self.assertEquals(l2_r.range, odl.RealNumbers())
        self.assertEquals(l2_c.range, odl.ComplexNumbers())

    def eq_test(self):
        intv = odl.Interval(0, 1)
        intv2 = odl.Interval(-1, 1)
        l2 = L2(intv)
        l2_r = L2(intv, field=odl.RealNumbers())
        l2_c = L2(intv, field=odl.ComplexNumbers())
        l2_intv2 = L2(intv2)

        self.assertEquals(l2, l2_r)
        self.assertNotEquals(l2, l2_c)
        self.assertNotEquals(l2, l2_intv2)


class L2VectorTest(ODLTestCase):

    @staticmethod
    def _points(domain, num):
        beg = domain.begin
        end = domain.end
        ndim = domain.ndim
        points = np.random.uniform(low=0, high=1, size=(num, ndim))
        for i in range(ndim):
            points[:, i] = beg[i] + (end[i] - beg[i]) * points[:, i]
        return points

    @staticmethod
    def _meshgrid(domain, shape):
        beg = domain.begin
        end = domain.end
        ndim = domain.ndim
        coord_vecs = []
        for i in range(ndim):
            vec = np.random.uniform(low=beg[i], high=end[i], size=shape[i])
            vec.sort()
            coord_vecs.append(vec)
        return np.meshgrid(*coord_vecs, indexing='ij', sparse=True,
                           copy=True)

    def init_test(self):
        # 1d, real
        intv = odl.Interval(0, 1)
        l2 = L2(intv)
        l2.element(func_1d)
        l2.element(func_1d, vectorization='none')
        l2.element(func_1d, vectorization='array')
        l2.element(func_1d, vectorization='meshgrid')
        l2.element(func_1d, func_1d_apply, vectorization='array')
        l2.element(func_1d, func_1d_apply, vectorization='meshgrid')

        with self.assertRaises(ValueError):
            l2.element(func_1d, func_1d_apply, vectorization='none')

        # 2d, real
        rect = odl.Rectangle([0, 0], [1, 2])
        l2 = L2(rect)
        l2.element(func_2d_novec)
        l2.element(func_2d_novec, vectorization='none')
        l2.element(func_2d_array, vectorization='array')
        l2.element(func_2d_mg, vectorization='meshgrid')
        l2.element(func_2d_array, func_2d_array_apply, vectorization='array')
        l2.element(func_2d_mg, func_2d_mg_apply, vectorization='meshgrid')

        with self.assertRaises(ValueError):
            l2.element(func_2d_novec, func_2d_array_apply,
                       vectorization='none')

        # 2d, complex
        l2 = L2(rect, field=odl.ComplexNumbers())
        l2.element(cfunc_2d_novec)
        l2.element(cfunc_2d_novec, vectorization='none')
        l2.element(cfunc_2d_array, vectorization='array')
        l2.element(cfunc_2d_mg, vectorization='meshgrid')
        l2.element(cfunc_2d_array, cfunc_2d_array_apply, vectorization='array')
        l2.element(cfunc_2d_mg, cfunc_2d_mg_apply, vectorization='meshgrid')

    def call_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        points = self._points(rect, num=50)
        mg = self._meshgrid(rect, shape=(5, 10))

        # real
        l2 = L2(rect)
        f_novec = l2.element(func_2d_novec)
        f_array = l2.element(func_2d_array, vectorization='array')
        f_mg = l2.element(func_2d_mg, vectorization='meshgrid')

        # non-vectorized
        for p in points:
            self.assertAlmostEquals(f_novec(p), func_2d_novec(p))
        # array version
        self.assertAllAlmostEquals(f_array(points), func_2d_array(points))
        # meshgrid version
        self.assertAllAlmostEquals(f_mg(mg), func_2d_mg(mg))

        with self.assertRaises(TypeError):
            f_novec(points)
        with self.assertRaises(TypeError):
            f_novec(mg)

        with self.assertRaises(ValueError):  # ValueError: wrong shape
            f_array(points[0])
        with self.assertRaises(TypeError):
            f_array(mg)

        with self.assertRaises(TypeError):
            f_mg(points[0])
        with self.assertRaises(ValueError):  # ValueError: wrong number of vecs
            f_mg(points)

        # complex
        l2 = L2(rect, field=odl.ComplexNumbers())
        f_novec = l2.element(cfunc_2d_novec)
        f_array = l2.element(cfunc_2d_array, vectorization='array')
        f_mg = l2.element(cfunc_2d_mg, vectorization='meshgrid')

        # non-vectorized
        for p in points:
            self.assertAlmostEquals(f_novec(p), cfunc_2d_novec(p))
        # array version
        self.assertAllAlmostEquals(f_array(points), cfunc_2d_array(points))
        # meshgrid version
        self.assertAllAlmostEquals(f_mg(mg), cfunc_2d_mg(mg))

        # Test bounds check
        points_outside_1 = np.array([[-1., 0], [0, 0]])
        points_outside_2 = np.array([[1., 0], [0, 2.5]])
        mg_outside_1 = np.meshgrid([-1, 0], [0.5, 1.5], indexing='ij',
                                   sparse=True, copy=True)
        mg_outside_2 = np.meshgrid([0, 0.5], [0.5, 3.5], indexing='ij',
                                   sparse=True, copy=True)

        with self.assertRaises(TypeError):
            f_novec([-1, 0])
        with self.assertRaises(TypeError):
            f_novec([0, 2.5])
        with self.assertRaises(ValueError):
            f_array(points_outside_1)
        with self.assertRaises(ValueError):
            f_array(points_outside_2)
        with self.assertRaises(ValueError):
            f_mg(mg_outside_1)
        with self.assertRaises(ValueError):
            f_mg(mg_outside_2)

        # Test disabling vectorized bounds check
        f_array(points_outside_1, vec_bounds_check=False)
        f_mg(mg_outside_1, vec_bounds_check=False)

    def apply_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        points = self._points(rect, num=50)
        mg = self._meshgrid(rect, shape=(5, 10))

        # real
        l2 = L2(rect)
        f_array = l2.element(func_2d_array, func_2d_array_apply,
                             vectorization='array')
        f_mg = l2.element(func_2d_mg, func_2d_mg_apply,
                          vectorization='meshgrid')

        # array version
        out = np.empty((50,), dtype=float)
        f_array.apply(points, out)
        self.assertAllAlmostEquals(out, func_2d_array(points))
        # meshgrid version
        out = np.empty((5, 10), dtype=float)
        f_mg.apply(mg, out)
        self.assertAllAlmostEquals(out, func_2d_mg(mg))

        out = np.empty((5,), dtype=float)  # wrong shape
        with self.assertRaises(ValueError):
            f_array.apply(points, out)
        with self.assertRaises(ValueError):
            f_mg.apply(mg, out)

        # complex
        l2 = L2(rect, field=odl.ComplexNumbers())
        f_array = l2.element(cfunc_2d_array, cfunc_2d_array_apply,
                             vectorization='array')
        f_mg = l2.element(cfunc_2d_mg, cfunc_2d_mg_apply,
                          vectorization='meshgrid')

        # array version
        out = np.empty((50,), dtype=complex)
        f_array.apply(points, out)
        self.assertAllAlmostEquals(out, cfunc_2d_array(points))
        # meshgrid version
        out = np.empty((5, 10), dtype=complex)
        f_mg.apply(mg, out)
        self.assertAllAlmostEquals(out, cfunc_2d_mg(mg))

    def eq_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        l2 = L2(rect)

        f_novec = l2.element(func_2d_novec)
        f_novec_2 = l2.element(func_2d_novec)

        f_array = l2.element(func_2d_array, vectorization='array')
        f_array_2 = l2.element(func_2d_array, vectorization='array')
        f_array_a = l2.element(func_2d_array, func_2d_array_apply,
                               vectorization='array')
        f_array_a_2 = l2.element(func_2d_array, func_2d_array_apply,
                                 vectorization='array')

        f_mg = l2.element(func_2d_mg, vectorization='meshgrid')
        f_mg_2 = l2.element(func_2d_mg, vectorization='meshgrid')
        f_mg_a = l2.element(func_2d_mg, func_2d_mg_apply,
                            vectorization='meshgrid')
        f_mg_a_2 = l2.element(func_2d_mg, func_2d_mg_apply,
                              vectorization='meshgrid')

        self.assertEquals(f_novec, f_novec)
        self.assertEquals(f_novec, f_novec_2)
        self.assertNotEquals(f_novec, f_array)
        self.assertNotEquals(f_novec, f_mg)

        self.assertEquals(f_array, f_array_2)
        self.assertEquals(f_array_a, f_array_a_2)
        self.assertNotEquals(f_array, f_array_a)
        self.assertNotEquals(f_array, f_mg)

        self.assertEquals(f_mg, f_mg_2)
        self.assertEquals(f_mg_a, f_mg_a_2)
        self.assertNotEquals(f_mg, f_mg_a)
        self.assertNotEquals(f_mg, f_array)

    def zero_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        points = self._points(rect, num=5)
        mg = self._meshgrid(rect, shape=(2, 3))

        # real
        l2 = L2(rect)

        zero_novec = l2.zero()
        zero_array = l2.zero(vectorization='array')
        zero_mg = l2.zero(vectorization='meshgrid')

        for p in points:
            self.assertEquals(zero_novec(p), 0.0)

        self.assertAllEquals(zero_array(points), np.zeros(5, dtype=float))
        self.assertAllEquals(zero_mg(mg), np.zeros((2, 3), dtype=float))

        # complex
        l2 = L2(rect, field=odl.ComplexNumbers())

        zero_novec = l2.zero()
        zero_array = l2.zero(vectorization='array')
        zero_mg = l2.zero(vectorization='meshgrid')

        for p in points:
            self.assertEquals(zero_novec(p), 0.0 + 1j*0.0)

        self.assertAllEquals(zero_array(points), np.zeros(5, dtype=complex))
        self.assertAllEquals(zero_mg(mg), np.zeros((2, 3), dtype=complex))

    def one_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        points = self._points(rect, num=5)
        mg = self._meshgrid(rect, shape=(2, 3))

        # real
        l2 = L2(rect)

        one_novec = l2.one()
        one_array = l2.one(vectorization='array')
        one_mg = l2.one(vectorization='meshgrid')

        for p in points:
            self.assertEquals(one_novec(p), 1.0)

        self.assertAllEquals(one_array(points), np.ones(5, dtype=float))
        self.assertAllEquals(one_mg(mg), np.ones((2, 3), dtype=float))

        # complex
        l2 = L2(rect, field=odl.ComplexNumbers())

        one_novec = l2.one()
        one_array = l2.one(vectorization='array')
        one_mg = l2.one(vectorization='meshgrid')

        for p in points:
            self.assertEquals(one_novec(p), 1.0 + 1j*0.0)

        self.assertAllEquals(one_array(points), np.ones(5, dtype=complex))
        self.assertAllEquals(one_mg(mg), np.ones((2, 3), dtype=complex))

    def lincomb_test(self):
        rect = odl.Rectangle([0, 0], [1, 2])
        points = self._points(rect, num=5)
        point = points[0]
        mg = self._meshgrid(rect, shape=(2, 3))

        # real
        l2 = L2(rect)
        a = -1.5
        b = 2.0
        f_novec = l2.element(func_2d_novec)
        g_novec = l2.element(other_func_2d_novec)
        out_novec = l2.element()

        # Test different optimized cases and alignments
        l2.lincomb(a, f_novec, b, g_novec, out_novec)


if __name__ == '__main__':
    pytest.main(str(__file__.replace('\\', '/') + ' -v'))

