'''
Created on Jan 27, 2013

@author: elazar
'''

class Singleton(type):
    _instances = None
    def __call__(self, *args, **kwargs):
        if self._instances:
            self._instances = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances
