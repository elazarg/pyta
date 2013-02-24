'''
Created on Jan 23, 2013

@author: elazar
'''



class SymTable:
    #constants = {'None' : st(NONE), 'False' : st(BOOL), 'True' : st(BOOL)}
    def __init__(self, enclosing = None):
        self.vars =  {}
        self.enclosing = enclosing
    
    def bind(self, var_id, typeset):
        assert isinstance(var_id, str)
        
        import typeset 
        ts = self.get_var(var_id, typeset.nts())
        if not ts:
            ts = self.vars[var_id] = typeset.nts()
        ts.update(typeset)

    def update(self, dic):
        for k, v in dic.items():
            self.bind(k, v)
    
    def merge(self, other):
        assert isinstance(other, SymTable)
        for k,v in other.vars.items():
            self.bind(k, v)
        
    def get_var(self, name, default = None):
        res = self.vars.get(name, None)
        if res != None:
            return res
        if self.enclosing==None:
            return default
        return self.enclosing.get_var(name, default)

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
            print('\t'*depth + '{0} : {1}'.format(k,v))
            for c in v:
                c.get_symtable().print(depth+1)
                
