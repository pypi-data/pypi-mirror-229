import pytest

from fofunction.map import Map

__author__ = "Jerome Douay"
__copyright__ = "Jerome Douay"
__license__ = "MIT"


def test_x_below():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[1,2]]

    map=Map(x,y,z)
    assert map.z(-1,0)==0

def test_y_below():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[2,3]]

    map=Map(x,y,z)
    assert map.z(0,-1)==0

def test_x_above():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[2,3]]

    map=Map(x,y,z)
    assert map.z(2,0)==2

def test_y_above():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[2,3]]

    map=Map(x,y,z)
    assert map.z(0,2)==1

def test_exact():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[2,3]]

    map=Map(x,y,z)
    assert map.z(0,0)==0
    assert map.z(0,1)==1
    assert map.z(1,0)==2
    assert map.z(1,1)==3

def test_interp():
    x=[0,1]
    y=[0,1]
    z=[[0,1],[2,3]]

    map=Map(x,y,z)
    assert map.z(0.5,0.5)==1.5
    #assert map.z(1.5,1.5)==1.5
