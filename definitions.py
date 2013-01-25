
from typeset import TypeSet, st, TObject
from symtable import SymTable
       
class TArguments():
    def __init__(self, arg, b = None):         
        rearg = [i.arg for i in arg.args]
        size = len(arg.defaults)
        self.pos = rearg[:-size] if size > 0 else rearg
        
        self.bind = b
        if b != None:
            del self.pos[0]
        
        self.defs = list(zip(rearg[-size:] , arg.defaults))        
        
        self.vararg = arg.vararg
        self.varargannotation = arg.varargannotation
        self.kwonlyargs = [i.arg for i in arg.kwonlyargs]
        self.kwarg = arg.kwarg
        self.kwargannotation = arg.kwargannotation
        self.kw_defaults = arg.kw_defaults
        
        self.names = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  
        
    def with_bind(self, t):
        return TArguments(self.arg, t)
        
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
        if self.kwarg == None and len(spare_keywords) > 0:
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
        
        return '({0})'.format( ', '.join(str(i) for i in [pos, defs, varargs, kws, kwargs, self.bind] if i) )

# TODO argslist as a class
class TFunc(TObject):
    def __init__(self, args, typefunc, t, bind = None):
        # assert isinstance(typefunc, (TypeSet, type(None)))
        self.orig_args = args
        
        self.t = t
        self.args = TArguments(args, bind)
        if t == None:
            self.typefunc = lambda *x : st(TObject(type(None)))
        else:
            self.typefunc = typefunc
    
    def __repr__(self):
        return self.t + ' {0} -> {1}'.format(self.args, self.typefunc())

    def with_bind(self, bind):
        return TFunc(self.orig_args, self.typefunc, self.t, bind)
        
    def ismatch(self, actual_args):
        res = self.args.ismatch(actual_args)
        if not res:
            import ast
            print(ast.dump(actual_args), 'does not match', repr(self.args))
        return res
        
    def call(self, actual_args):
        if not self.ismatch(actual_args):
            return TypeSet({})
        return self.typefunc(actual_args)


class TClass(TObject):
    def __init__(self, name, bases, keywords, starargs, kwargs):
        self.name, self.bases = name, bases
        self.keywords, self.starargs, self.kwargs = keywords, starargs, kwargs
        self.namespace = SymTable()
        self.type = self #should be 'TType'
        self.id = TObject(self.bases, self)
        
    def update_namespace(self, sym):
        self.namespace.merge(sym)
    
    def __repr__(self):
        return "Class: '{0}'".format(self.name)
    
    def get_type_attr(self, name):
        return self.namespace.get_var(name, None) 
    
    def ismatch(self, args):
        x = self.namespace.get_var('__init__', None)
        if x == None:
            return len(args.args)==0
        return x.ismatch(args)
    
    def call(self, args):
        #TODO : match signature
        return st(self.new_instance())
    
    def new_instance(self):
        "like call, but don't bother with signature"
        return self.id
    
if __name__=='__main__':
    import analyze
    analyze.main()    