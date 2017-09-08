'''
Created on 19 Apr 2013

@author: theo
'''
import adore

class Tesnet(object):
    '''
    classdocs
    '''

    def __init__(self, filename=None):
        '''
        Constructor
        '''
        if filename is not None:
            self.load(filename)
            
    def load(self, filename):
        self.teo = adore.AdoreCollection(filename)
        x = self.teo.get_values('X-COORDINATES')        
        y = self.teo.get_values('Y-COORDINATES')
        e1 = self.teo.get_values('ELEMENT NODES 1')
        e2 = self.teo.get_values('ELEMENT NODES 2')
        e3 = self.teo.get_values('ELEMENT NODES 3')
        b = self.teo.get_values('LIST BOUNDARY NODES')
        s = self.teo.get_values('SOURCE NODES')
        sn = self.teo.get_values('SOURCE NUMBERS')
        nr = self.teo.get_values('NUMBER NODES/RIVER')
        r = self.teo.get_values('LIST RIVER NODES')
        rn = self.teo.get_values('RIVER NUMBERS')
