from types import Instance, Class, TypeSet, ANY
       
class Arguments():
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
        return Arguments(self.arg, t)
        
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

    def tostr(self):
        pos = ', '.join(self.pos)
        defs = ', '.join('{0}={1}'.format(k,v.tostr()) for k,v in self.defs)
        varargs = None
        if self.vararg:
            varargs = '*' + self.vararg
            if self.varargannotation:
                varargs += ':' + repr(self.varargannotation)
        kws = ', '.join(('{0}={1}'.format(k, v.tostr()) if v else k) for k, v in zip(self.kwonlyargs, self.kw_defaults))
        kwargs = '**' + self.kwarg if self.kwarg else None
        
        return '({0})'.format( ', '.join(i if isinstance(i, str) else i.tostr() for i in [pos, defs, varargs, kws, kwargs, self.bind] if i) )


FUNCTION = Class('function') 

'''
should make distinction between types of variables in general,
and return type of some specific execution place
'''
class Function(Instance):
    def __init__(self, args, typefunc, name, bind = None):
        # assert isinstance(typefunc, (TypeSet, type(None)))
        Instance.__init__(self, FUNCTION)
        self.orig_args = args
        self.name = name
        self.args = Arguments(args, bind)
        if typefunc == None:
            self.typefunc = lambda *x : Instance(type(None))
        else:
            self.typefunc = typefunc
    
    def tostr(self):
        from ast import Call, Name, Load
        c = Call(func=Name(id='x', ctx=Load()), args=[TypeSet({})], keywords=[], starargs=None, kwargs=None)
        return ' {0} -> {1}'.format(self.args.tostr(), self.typefunc(c).tostr())

    def bind_parameter(self, bind):
        return Function(self.orig_args, self.typefunc, self.name, bind)
        
    def ismatch(self, actual_args):
        res = self.args.ismatch(actual_args)
        if not res:
            import ast
            print(ast.dump(actual_args))
            print('does not match', repr(self.args))
        return res
        
    def call(self, actual_args):
        if not self.ismatch(actual_args):
            return TypeSet({})
        return self.typefunc(actual_args)
    @staticmethod
    def get_generic():
        from ast import arguments
        args = arguments(args=[], vararg=None, varargannotation=None, kwonlyargs=[], kwarg=None, kwargannotation=None, defaults=[], kw_defaults=[])
        res = Function(args, lambda x : ANY, '@generic')
        res.args.ismatch = lambda *x : True
        return res

FUNCTION.instance = Function.get_generic()

if __name__=='__main__':
    import analyze
    analyze.main()    