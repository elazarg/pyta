from typeset import TypeSet, st
from itertools import product

class TObject:
    def __init__(self, t=object):
        self.type = t
        self.dict = {}

    def __repr__(self):
        return repr(self.type).split(sep="'")[1]
            
    
class TNum(TObject):
    def __init__(self, t):
        self.dict = {}
    
    def get_dict(self):
        return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())}

    def __repr__(self):
        return "num"     

class TInt(TNum):
    def __init__(self, t=int):
        pass
    
    def __repr__(self):
        return "int"

class TBool(TNum):
    def __init__(self, t=int):
        self.dict = TInt().dict

    def __repr__(self):
        return "bool"

class TFloat(TNum):
    def __init__(self, t=float):
        pass
    
    def __repr__(self):
        return "float"

class TSeq(TObject):
    def __init__(self, *targs):
        self.dict = TObject().dict
        self.types = set(targs)
    
    def typeset(self):
        return self.types

    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [self.types] * n
    
    @staticmethod
    def fromset(keyset):
        res = TSeq()
        res.update(keyset)
        return res
    
    def add(self, t):
        self.types.add(t)
    
    def update(self, tlist):
        self.types.update(tlist)
    
    def __repr__(self):
        return "Seq(" + repr(self.types) + ")"

    def get_dict(self):
        return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())} 


class TIter(TSeq):
    def __repr__(self):
        return "Iter(" + repr(self.types) + ")"

class TDict(TSeq):
    def __init__(self, tkeys, tvalues):
        self.dict = {}            
        skeys = TypeSet.union_all(tkeys) if len(tkeys) != 0 else TypeSet({})
        temp = set(sum([list(product(k, v)) for k, v in zip(tkeys, tvalues)], []))
        self.types = { k : TypeSet([v for tk, v in temp if tk == k]) for k in skeys}
    
    def __repr__(self):
        return "Dict(" + repr(self.types) + ")"

class TTuple(TSeq):
    def __init__(self, tvalues):
        self.types = tuple(tvalues)
        self.dict = TObject().dict
   
    def __len__(self):
        return len(self.types)
 
    def can_split_to(self, n):
        return len(self.types) == n
    
    def split_to(self, n):
        assert len(self.types) == n
        return self.types 
 
    def typeset(self):   
        return TypeSet.union_all(self.types)
       
    def __repr__(self):
        return repr(self.types)

    def get_dict(self):
        return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())} 


class TList(TTuple):
    def __repr__(self):
        return repr(list(self.types))
    
class TSet(TTuple):
    def __repr__(self):
        return "Set(" + repr(self.types) + ")"
    
class TStr(TTuple):
    def __init__(self, t): 
        self.t = t
    
    def __repr__(self):
        return repr(self.t).split("'")[1]
    
    def typeset(self):   
        return st(TStr())

       
class TArguments():
    '''
    >>> ast.dump(ast.parse('def foo(a ,b1=5, *c, b2=0, **d): pass').body[0].args)
    "arguments(
    args=[arg(arg='a',        annotation=None),
          arg(arg='b1',       annotation=None)],
    vararg='c',               varargannotation=None,
    kwonlyargs=[arg(arg='b2', annotation=None)],
    kwarg='d',                kwargannotation=None,
    defaults=[Num(n=5)],
    kw_defaults=[Num(n=0)])"
    '''
    def __init__(self, arg):
        rearg = [i.arg for i in arg.args]
        size = len(arg.defaults)
        self.pos = rearg[:-size] if size > 0 else rearg
        self.defs = list(zip(rearg[-size:] , arg.defaults))        
        #self.args = [i.arg for i in arg.args]
        #self.defaults = arg.defaults
        
        self.vararg = arg.vararg
        self.varargannotation = arg.varargannotation
        self.kwonlyargs = [i.arg for i in arg.kwonlyargs]
        self.kwarg = arg.kwarg
        self.kwargannotation = arg.kwargannotation
        self.kw_defaults = arg.kw_defaults
        
        self.names = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  
        
    '''    
    >>> ast.dump(ast.parse('foo(z,y=6,*[1])').body[0].value)
    "Call(    func=Name(id='foo', ctx=Load()),
    args=[Name(id='z', ctx=Load())],
    keywords=[keyword(arg='y', value=Num(n=6))],
    starargs=List(elts=[Num(n=1)], ctx=Load()),
    kwargs=None)"
    '''
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
        
        return '(' + ', '.join(i for i in [pos, defs, varargs, kws, kwargs] if i) + ')'

# TODO argslist as a class
class TFunc(TObject):
    def __init__(self, args, returns, t):
        self.t = t
        self.args = TArguments(args)
        assert isinstance(returns, TypeSet)
        self.returns = returns
    
    def __repr__(self):
        return self.t + ' {0} -> {1}'.format(repr(self.args), self.returns)
        
    def ismatch(self, actual_args):
        res = self.args.ismatch(actual_args)
        if not res:
            import ast
            print(ast.dump(actual_args), 'does not match', repr(self.args))
        return res
        
    def call(self, actual_args):
        assert self.ismatch(actual_args)
        return self.returns
    
BOOL = TObject(bool)
STR = TStr(str)
BYTES = TStr(bytes)
INT, FLOAT, COMPLEX = TInt(), TFloat(), TNum(complex)
NONE = TObject(type(None))
