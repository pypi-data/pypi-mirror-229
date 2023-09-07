import pytest

from src.fofunction.curve import Curve

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"


def test_y_below():
    x=[0,1,2,3,4,5]
    y=[0,1,2,3,4,6]
    curve=Curve(x,y)
    assert curve.y(-1)==0

def test_y_above():
    x=[0,1,2,3,4,5]
    y=[0,1,2,3,4,6]
    curve=Curve(x,y)
    assert curve.y(6)==5

def test_y_exact():
    x=[0,1,2,3,4,5]
    y=[0,1,2,3,4,6]
    curve=Curve(x,y)
    assert curve.y(0)==0
    assert curve.y(1)==1
    assert curve.y(2)==2
    assert curve.y(3)==3
    assert curve.y(4)==4
    assert curve.y(5)==5

def test_y_interpolate():
    x=[0,1,2,3,4,5]
    y=[0,1,2,3,4,6]
    curve=Curve(x,y)
    assert curve.y(0.5)==0.5
