'''
Created on Jan 23, 2013

@author: elazar
'''
from typeset import TypeSet, st, NONE, BOOL

class SymTable:
    constants = {'None' : st(NONE), 'False' : st(BOOL), 'True' : st(BOOL)}
    def __init__(self):
        self.vars =  {}
    
    def bind(self, var_id, typeset):
        assert isinstance(typeset, TypeSet)
        assert isinstance(var_id, str)
        
        ts = self.get_var(var_id, TypeSet({}))
        if not ts:
            ts = self.vars[var_id] = TypeSet({})
        ts.update(typeset)

    def merge(self, other):
        assert isinstance(other, SymTable)
        for k,v in other.vars.items():
            self.bind(k, v)
        
    def get_var(self, name, default = 0):
        #prior 3.4: 
        #consts = SymTable.constants.get(name, TypeSet({}))
        #return self.vars.get(name, TypeSet({})).union(consts)
        return self.vars.get(name, default)

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
    
    def print(self):
        for k,v in self.vars.items():
            print('{0} : {1}'.format(k,v))
