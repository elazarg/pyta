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
        return {i:j for i,j in list(self.dict.items())+list(super.get_dict(self).items())}

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
        self.dict=TObject().dict
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
        return "Seq(" + repr(self.types) +")"

    def get_dict(self):
        return {i:j for i,j in list(self.dict.items())+list(super.get_dict(self).items())} 


class TIter(TSeq):
    def __repr__(self):
        return "Iter(" + repr(self.types) +")"

class TDict(TSeq):
    def __init__(self, tkeys, tvalues):
        self.dict = {}            
        skeys = TypeSet.union_all(tkeys) if len(tkeys) != 0 else TypeSet({})
        temp = set(sum([list(product(k,v)) for k,v in zip(tkeys, tvalues)], []))
        self.types = { k : TypeSet([v for tk, v in temp if tk==k]) for k in skeys}
    
    def __repr__(self):
        return "Dict(" + repr(self.types) +")"

class TTuple(TSeq):
    def __init__(self, tvalues):
        self.types = tuple(tvalues)
        self.dict=TObject().dict
   
    def __len__(self):
        return len(self.types)
 
    def can_split_to(self, n):
        return len(self.types)==n
    
    def split_to(self, n):
        assert len(self.types)==n
        return self.types 
 
    def typeset(self):   
        return TypeSet.union_all(self.types)
       
    def __repr__(self):
        return repr(self.types)

    def get_dict(self):
        return {i:j for i,j in list(self.dict.items())+list(super.get_dict(self).items())} 


class TList(TTuple):
    def __repr__(self):
        return repr(list(self.types))
    
class TSet(TTuple):
    def __repr__(self):
        return "Set(" + repr(self.types) +")"
    
class TStr(TTuple):
    def __init__(self, t): 
        self.t = t
    
    def __repr__(self):
        return repr(self.t).split("'")[1]
    
    def typeset(self):   
        return st(TStr())

class TArgs:
    def __init__(self, argslist):
        assert len(argslist) == 8
        self.args, self.vararg, self.varargannotation = argslist[:3]
        self.argnames = [i.arg for i in self.args]
        self.kwonlyargs, self.kwarg, self.kwargannotation = argslist[3:6]
        self.defaults, self.kw_defaults = argslist[6:]
        
    def __repr__(self):
        regargs = self.argnames[:-len(self.defaults)]+['{0}={1}'.format(i,j) for i,j in zip(reversed(self.argnames), reversed(self.defaults))]
        res = (i for i in (regargs, self.vararg, self.varargannotation, self.kwonlyargs, self.kwarg, self.kwargannotation, self.kw_defaults) if i)
        return str(tuple(res))

    def ismatch(self, actual_args):
        return len(self.args)==len(actual_args)
       
#TODO argslist as a class
class TFunc(TObject):
    def __init__(self, name, argslist, returns):
        self.name = name
        self.formal_params = TArgs(argslist)
        assert isinstance(returns, TypeSet)
        self.returns = returns
    
    def __repr__(self):
        return '{0}{1} -> {2}'.format(self.name, repr(self.formal_params), self.returns)
    
    def ismatch(self, actual_args):
        return self.formal_params.ismatch(actual_args)

    def call(self, actual_args):
        assert self.ismatch(actual_args)
        return self.returns

class TClass(TObject):
    def __init__(self, name, bases, keywords, starargs, kwargs):
        self.name, self.bases = name, bases
        self.keywords, self.starargs, self.kwargs = keywords, starargs, kwargs
        self.namespace = {}
        
    def update_namespace(self, dic):
        self.namespace.update(dic)
    
    def __repr__(self):
        attrepr = repr({i:j for i,j in self.namespace.items() if i != self.name})
        return 'Class: {0}[{1}]'.format(self.name, attrepr) 
    

BOOL = TObject(bool)
STR = TStr(str)
BYTES = TStr(bytes)
INT, FLOAT, COMPLEX = TInt(), TFloat(), TNum(complex)
NONE = TObject(type(None))
