'''
Created on Jan 23, 2013

@author: elazar
'''
from typeset import TypeSet, st
from types import NONE, BOOL

class SymTable:
    constants = {'None' : st(NONE), 'False' : st(BOOL), 'True' : st(BOOL)}
    def __init__(self):
        self.vars =  [{}]

    def push(self, top={}):
        self.vars.append(top)

    def pop(self):
        return self.vars.pop()
    
    def depth(self):
        return len(self.vars)
    
    def popmerge(self):
        d = self.pop()
        for k,v in d.items():
            self.update(k, v)
        return d
    
    def update(self, var_id, valset):
        ts = self.get_var(var_id)
        if len(ts)==0:
            ts = self.vars[-1][var_id] = TypeSet({})
        ts.update(valset)

    def update_func(self, fname, func):
        return self.update(fname, st(func))
        
    def merge(self, other):
        assert isinstance(other, SymTable)
        for d in other.vars:
            for k,v in d.items():
                self.update(k, v)
        
    def get_var(self, name):
        #prior 3.4: 
        #consts = SymTable.constants.get(name, TypeSet({}))
        #return self.vars.get(name, TypeSet({})).union(consts)
        for d in self.vars:
            if name in d:
                return d[name]
        return TypeSet({}) 

    def __getitem__(self, name):
        return self.get_var(name)

    def __repr__(self):
        return '{0}'.format(repr(self.vars))
    
    def __eq__(self, other):
        return isinstance(other, SymTable) and self.vars == other.vars
    
    def __len__(self):
        return sum(len(d) for d in self.vars)
    
    def includes(self, other):
        return isinstance(other, SymTable) and self.vars == other.vars
