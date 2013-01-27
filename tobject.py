from symtable import SymTable
from typeset import TypeSet

class TObject:
    def __init__(self, s=None, t=None, sym = None):
        if t == None and s != None:
            t = type(s)
        self.type = t
        self.s = s
        if sym == None:
            self.instance_vars = SymTable()
        else:
            self.instance_vars = sym

    def __repr__(self):
        return repr(self.type).split(sep="'")[1]
    
    def get_symtable(self):
        return self.instance_vars
    
    def has_type_attr(self, attr):
        res = self.get_type_attr(attr)
        return res != None
        
    def get_type_attr(self, attr):
        res = self.instance_vars.get_var(attr)
        if res == None:
            if self.s == None:
                'no such instane variable - return class variable'
                res = TypeSet({a.with_bind(self) for a in self.type.get_type_attr(attr)})
            else:
                #res = self.s.get_type_attr(attr)
                pass
        return res

    def weak_bind(self, var_id, typeset):
        self.instance_vars.bind(var_id, typeset)
    
    def ismatch(self, actual_args):
        return False
    
    def with_bind(self, x):
        '''binds nothing for objects'''
        return self

BOOL = TObject(TObject, bool)
NONE = TObject(TObject, type(None))
