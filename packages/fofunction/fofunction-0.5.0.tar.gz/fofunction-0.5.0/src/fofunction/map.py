#  Copyright (c) 2017-2021 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import pandas
import numpy
import logging
from scipy.interpolate import LinearNDInterpolator

from .curve import Curve
from .axis import Axis
"""
map Class
"""
# import itertools


class Map(object):
    """
    Map allow the defintion and extroplation of data of a map

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self, x, y, z,name='map',log=logging.INFO):
        self.name=name
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name+'_x')

        if isinstance(y, Axis):
            self._y = y
        else:
            self._y = Axis(y, name+'_y')
        self._z = z

        self._points()
        self._interp()
        self.log = logging.getLogger(self.__class__.__module__)
        self.log.setLevel(log)


    def z(self, x, y):
        """
        return the y value of a curve given the x value.
        Values are interpolated between the points given
        """
        return self.f(x, y)

    def table(self, x, y):
        '''
        Generate a table based on x and y axis
        '''
        z = []
        for vy in y:
            ys = []
            for vx in x:
                ys.append(self.z(x, y))
            z.append(ys)

        return z

    def xz(self, y):
        ys = []
        for x in self._x:
            ys.append(self.z(x, y))
        return Curve(self._x, ys)

    # TODO def zx

    def yz(self, x):
        xs = []
        for y in self._y:
            xs.append(self.z(x, y))
        return Curve(xs, self._y)

    # TODO def zy
    
    def update(self, x, y, z, z_min, z_max, weight=1):
        '''
        update z value at x,y position. The table size is not changed but the points are refitted to match the change.
        '''
        # TODO generate warning / error when points are outise the table boundaries
        delta=(z-self.z(x,y))/weight

        for iy in range(len(self._y.values)):
            dy=y-self._y.values[iy]
            for ix in range(len(self._x.values)):
                dx=x-self._x.values[ix]
                dist=(dx**2+dy**2)**0.5
                alpha=numpy.arctan(dist/delta)
                self._z[iy][ix]+=numpy.cos(alpha)*delta
                self._z[iy][ix]=max(self._z[iy][ix],z_min)
                self._z[iy][ix]=min(self._z[iy][ix],z_max)

        self._points()
        self._interp()

    def _interp(self):
        points = self.points[['x', 'y']].values
        values = self.points['z']
        self.f = LinearNDInterpolator(points, values)

    def _points(self):
        self.points = pandas.DataFrame()
        xs = []
        ys = []
        zs = []
        for ix in range(0, len(self._x.values), 1):
            for iy in range(0, len(self._y.values), 1):
                xs.append(self._x.values[ix])
                ys.append(self._y.values[iy])
                zs.append(self._z[iy][ix])

        self.points['x'] = xs
        self.points['y'] = ys
        self.points['z'] = zs
