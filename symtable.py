'''
Created on Jan 23, 2013

@author: elazar
'''

import targettypes as types
class SymTable:
    def __init__(self):
        self.vars =  {}
    
    def bind_type(self, var_id, anInstance):
        assert isinstance(var_id, str)
        assert anInstance is not None
        
        self.vars[var_id] = types.meet(self.get_var(var_id), anInstance)
        assert self.vars[var_id] is not None
        
    def get_var(self, name):
        return self.vars.get(name, types.EMPTY())

    def __getitem__(self, name):
        return self.get_var(name)

    def __repr__(self):
        return '{0}'.format(repr(self.vars))
    
    def __eq__(self, other):
        return isinstance(other, SymTable) and set(self.vars.items) == set(other.vars.items())
    
    def __len__(self):
        return len(self.vars)
    
    def includes(self, other):
        if not isinstance(other, SymTable):
            return False
        if not set(self.keys()).issuperset(set(other.keys())):
            return False  
        for s in set(self.vars.keys()).intersection(set(other.vars.keys())):
            if not self.vars[s].contains(other.vars[s]):
                return False
        return True
    
    def print(self, depth=0):
        for k,v in self.vars.items():
            print('\t'*depth + '{0} : {1}'.format(k,v.tostr()))
                
