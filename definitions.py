from targettypes import Instance, Class, TypeSet


FUNCTION = Class('function') 

'''
should make distinction between types of variables in general,
and return type of some specific execution place
'''
class Function(Instance):
    def __init__(self, gnode, bound_arg=None):
        # assert isinstance(typefunc, (TypeSet, type(None)))
        Instance.__init__(self, FUNCTION)
        self.gnode = gnode
        self.bound_arg = bound_arg
    
    def tostr(self):
        ret = self.gnode.sym['return']
        return '{0}{1} -> {2}'.format(self.gnode.name, self.gnode.args.tostr(),
                                   ret.tostr())

    def bind_parameter(self, bind):
        return Function(self.gnode, bind)
        
    def ismatch(self, actual_args):
        res = self.gnode.args.match(actual_args) is not None 
        if not res:
            import ast
            print(ast.dump(actual_args))
            print('does not match', repr(self.gnode.args))
        return res
        
    def call(self, actual_args):
        dic = self.gnode.args.match(actual_args, self.bound_arg)
        if dic is None:
            return TypeSet({})
        self.gnode.bind_arguments(dic)
        return self.gnode.sym['return']
    
    @staticmethod
    def get_generic():
        from ast import parse
        #args = arguments(args=[], vararg=None, varargannotation=None, kwonlyargs=[], kwarg=None, kwargannotation=None, defaults=[], kw_defaults=[])
        func = parse('def foo(*x, **y): pass').body[0]
        func.sym = {}
        res = Function(func, None)
        res.ismatch = lambda *x : True
        return res

FUNCTION.instance = Function.get_generic()

if __name__=='__main__':
    import analyze
    analyze.main()    