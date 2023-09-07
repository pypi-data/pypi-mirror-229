#  Copyright (c) 2017-2023 Jeorme Douay <jerome@far-out.biz>
#  All rights reserved.

import numpy

from .axis import Axis

"""
Curve Class
"""


class Curve(object):
    """
    Curve allow the defintion and extroplation of data of a curve

    This class is usually returned by the DCM class after importing a file.
    """

    def __init__(self, x: Axis, y, name='curve'):
        if isinstance(x, Axis):
            self._x = x
        else:
            self._x = Axis(x, name+'_x')
    
        self._y = y  # array of values
        self.name=name

    def y(self, x):
        """
        return the y value of a curve given the x value.

        Values are interpolated between the points given
        """
        return numpy.interp(x,self._x.values,self._y)

    def update(self, x, y, y_min, y_max, weight=1):
        '''
        update the curve using the x,y supplied
        '''

        delta=(y-self.y(x))/weight
        for i in range(len(self._x.values)):
            _x=self._x.values[i]    
            alpha=numpy.arctan((_x-x)/delta)
            self._y[i]+=numpy.cos(alpha)*delta
            self._y[i]=max(self._y[i],y_min)
            self._y[i]=min(self._y[i],y_max)

