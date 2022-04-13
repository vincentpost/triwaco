"""
Created on 19 Apr 2013
Modified Apr 13, 2022 for python 3

@author: theo
"""
from .adore import AdoreCollection
import numpy as np


class Tesnet(AdoreCollection):
    """ Triwaco network file (tesnet output) """

    def nodes(self):
        x = self['X-COORDINATES'].get_values()
        y = self['Y-COORDINATES'].get_values()
        return np.array((x, y)).T

    def elements(self):
        e1 = self['ELEMENT NODES 1'].get_values()
        e2 = self['ELEMENT NODES 2'].get_values()
        e3 = self['ELEMENT NODES 3'].get_values()
        return np.array((e1, e2, e3)).T
