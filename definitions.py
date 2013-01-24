
from typeset import TypeSet, st
from symtable import SymTable
from types import TObject, NONE
       
class TArguments():
    def __init__(self, arg):
        rearg = [i.arg for i in arg.args]
        size = len(arg.defaults)
        self.pos = rearg[:-size] if size > 0 else rearg
        self.defs = list(zip(rearg[-size:] , arg.defaults))        
        
        self.vararg = arg.vararg
        self.varargannotation = arg.varargannotation
        self.kwonlyargs = [i.arg for i in arg.kwonlyargs]
        self.kwarg = arg.kwarg
        self.kwargannotation = arg.kwargannotation
        self.kw_defaults = arg.kw_defaults
        
        self.names = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  
        
    def ismatch(self, actual):
        bind = {}
        bind.update(zip(self.pos, actual.args))
        for keyword in actual.keywords:
            if keyword.arg in bind:
                # double assignment
                print('double assignment: ', keyword.arg)
                return False
            bind[keyword.arg] = keyword.value
        bind.update(self.defs)                        
        leftover = set(self.pos) - set(bind.keys())
        if len(leftover) > 0:
            # positional parameter left
            print('positional parameter left:', leftover)
            return False
        for k, v in zip(self.kwonlyargs, self.kw_defaults):
            if k not in bind and v != None:
                bind[k] = v
        leftover_keys = set(self.kwonlyargs).difference(bind.keys())
        if len(leftover_keys) > 0:
            # keyword-only parameter left
            print('keyword-only parameter left:', leftover_keys)
            return False
        spare_keywords = set(bind.keys()) - self.names
        if self.kwarg != None and len(spare_keywords) > 0:
            # keyword-only parameter left
            print('too many keyword arguments', spare_keywords)
            return False            
        return True

    def __repr__(self):
        pos = ', '.join(self.pos)
        defs = ', '.join('{0}={1}'.format(k,v) for k,v in self.defs)
        varargs = None
        if self.vararg:
            varargs = '*' + self.vararg
            if self.varargannotation:
                varargs += ':' + repr(self.varargannotation)
        kws = ', '.join(('{0}={1}'.format(k, v) if v else k) for k, v in zip(self.kwonlyargs, self.kw_defaults))
        kwargs = '**' + self.kwarg if self.kwarg else None
        
        return '({0})'.format( ', '.join(i for i in [pos, defs, varargs, kws, kwargs] if i) )

# TODO argslist as a class
class TFunc(TObject):
    def __init__(self, args, returns, t):
        assert isinstance(returns, (TypeSet, type(None)))
        self.t = t
        self.args = TArguments(args)
        if t == None:
            self.returns = st(NONE)
        else:
            self.returns = returns
    
    def __repr__(self):
        return self.t + ' {0} -> {1}'.format(self.args, self.returns)
        
    def ismatch(self, actual_args):
        res = self.args.ismatch(actual_args)
        if not res:
            import ast
            print(ast.dump(actual_args), 'does not match', repr(self.args))
        return res
        
    def call(self, actual_args):
        assert self.ismatch(actual_args)
        return self.returns


class TClass(TObject):
    def __init__(self, name, bases, keywords, starargs, kwargs):
        self.name, self.bases = name, bases
        self.keywords, self.starargs, self.kwargs = keywords, starargs, kwargs
        self.namespace = SymTable()
        
    def update_namespace(self, sym):
        self.namespace.merge(sym)
    
    def __repr__(self):
        return 'Class: {0}'.format(self.name)
    
    def get_type_attr(self, name):
        return self.namespace.get_var(name) 
    
    def has_type_attr(self, name):
        return len(self.namespace.get_var(name)) > 0 
    
    def call(self, args):
        return st(self)
