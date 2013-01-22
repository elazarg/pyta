from typeset import TypeSet, st, Empty, Any
from itertools import product

class TObject:
    def __init__(self, t=object):
        self.type = t
        self.dict = dict.fromkeys(['__eq__', '__ge__', '__le__', '__lt__', '__ne__', '__gt__'], lambda x : st(bool))
        self.dict['__class__'] = lambda : st(NONE)
        self.dict['__delattr__'] = lambda x : st(NONE)
        self.dict['__setattr__'] = lambda x : st(NONE)
        self.dict['__sizeof__']  = lambda : st(INT)
        self.dict['__doc__'] = lambda : st(TSeq([st(STR)]))
        self.dict['__repr__'] = lambda x : st(STR)
        self.dict['__str__'] = lambda x : st(STR)
        self.dict['__hash__']= lambda x : st(STR)
        self.dict['__init__'] = lambda *x : st(self)
        self.dict['__new__'] = lambda *x : st(self)

    def __repr__(self):
        return repr(self.type).split(sep="'")[1]
            
    
class TNum(TObject):
    def __init__(self, t):
        self.dict = {}
        self.dict.fromkeys(['__rpow__', '__rtruediv__', '__mod__', '__radd__', '__truediv__', '__sub__',
                             '__rfloordiv__', '__pow__', '__add__', '__floordiv__', '__rmul__', '__rsub__',
                              '__rmod__', '__float__', '__mul__'], lambda x, y : st(TNum()))
        self.dict['__bool__'] = lambda : st(TObject(bool))
        self.dict.update(dict.fromkeys(['__abs__','__neg__','conjugate'], lambda x : st(self)))
        self.dict.update(dict.fromkeys(['__ceil__','bit_length','denominator','numerator', 'real',
                             '__invert__','__round__','__trunc__'], lambda : st(TNum())))
        self.dict['__int__'] = lambda x : st(INT)
        self.dict['imag'] = lambda x : st(TNum(complex) )
        self.dict['from_bytes'] = lambda x : st(TNum())
        self.dict['to_bytes'] = lambda x : st(TObject(bytes))
    
    def get_dict(self):
        return {i:j for i,j in list(self.dict.items())+list(super.get_dict(self).items())}

    def __repr__(self):
        return "num"     

class TInt(TNum):
    def __init__(self, t=int):
        self.dict = dict.fromkeys(['__rshift__', '__rand__', '__ror__', '__xor__', '__floor__', '__rlshift__','__lshift__'
                             , '__and__', '__rrshift__', '__rxor__', '__or__'], lambda x, y : st(INT))
        self.dict['__divmod__']=self.dict['__rdivmod__'] = lambda x,y : st(TTuple([st(INT), st(INT)]))

    def __repr__(self):
        return "int"

class TBool(TNum):
    def __init__(self, t=int):
        self.dict = TInt().dict

    def __repr__(self):
        return "bool"

class TFloat(TNum):
    def __init__(self, t=float):
        self.dict = {}
        self.dict['fromhex'] = lambda x : st(self)
        self.dict['hex'] = lambda : st(STR)
        self.dict['as_integer_ratio'] = lambda x : st(TTuple([st(INT), st(INT)]))
        self.dict['is_integer'] = lambda : st(BOOL)

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
        self.dict = {}
        self.dict.update(dict.fromkeys(['sort', '__setitem__', 'extend', '__delitem__', 'append', 'reverse'],
                            lambda : st(type(None))))
        
        self.dict.update(dict.fromkeys(['index', '__len__', 'count'], lambda x : st(INT)))
        self.dict.update(dict.fromkeys(['remove', 'insert'],lambda x : st(type(None))) )
        
        self.dict.update(dict.fromkeys(['__getitem__', 'pop'], self.typeset))
        self.dict['is_integer'] = lambda : st(TObject(bool))
        self.dict.update(dict.fromkeys(['__reversed__', '__iter__'], lambda : st(self)))
        self.dict.update(dict.fromkeys(['__imul__', '__add__', '__rmul__' , '__mul__','__iadd__'],
                            lambda x : st(TSeq(self.typeset()))) )
        self.types = tuple(tvalues)
   
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

BOOL = TObject(bool)
STR = TStr(str)
BYTES = TStr(bytes)
INT, FLOAT, COMPLEX = TInt(), TFloat(), TNum(complex)
NONE = TObject(type(None))
