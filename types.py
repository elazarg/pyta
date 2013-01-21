from itertools import product
from functools import reduce

def TASSERT(b): 
    if not b:
        print('ERROR')

def st(t):
    return TypeSet({t})

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
        return "Num"     

class TInt(TNum):
    def __init__(self, t=int):
        self.dict = dict.fromkeys(['__rshift__', '__rand__', '__ror__', '__xor__', '__floor__', '__rlshift__','__lshift__'
                             , '__and__', '__rrshift__', '__rxor__', '__or__'], lambda x, y : st(INT))
        self.dict['__divmod__']=self.dict['__rdivmod__'] = lambda x,y : st(TTuple([st(INT), st(INT)]))

    def __repr__(self):
        return "Int"

class TBool(TNum):
    def __init__(self, t=int):
        self.dict = TInt().dict

    def __repr__(self):
        return "Bool"



class TFloat(TNum):
    def __init__(self, t=float):
        self.dict = {}
        self.dict['fromhex'] = lambda x : st(self)
        self.dict['hex'] = lambda : st(STR)
        self.dict['as_integer_ratio'] = lambda x : st(TTuple([st(INT), st(INT)]))
        self.dict['is_integer'] = lambda : st(BOOL)

    def __repr__(self):
        return "Float"

class AnyClass(TObject):
    def __init__(self):
        super(type)
        
    def __repr__(self):
        return "Any"
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{Any}] * n

Any = AnyClass()

class TypeSet(TObject):
    def __init__(self, iterable):
        assert not isinstance(iterable, TypeSet)
        self.types = set(iterable)
        self.to_invariant()
        
    def update(self, iterable):
        self.types.update(iterable)
        self.to_invariant()
        
    def add(self, obj):
        assert not isinstance(obj, TypeSet)
        self.types.add(obj)
        self.to_invariant()
    
    def to_invariant(self):
        if Any in self.types:
            self.types = {Any}
    
    def __iter__(self):
        return self.types.__iter__()
    
    @staticmethod
    def union_all(iterable):
        return TypeSet(set.union(*[i.types for i in iterable]))
    
    def __repr__(self):
        return 'T'+repr(self.types)

    def __len__(self):
        return len(self.types)
 

class BottomType:
    def __repr__(self):
        return "Bottom"

Bottom = BottomType()

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
        self.types = tvalues
   
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
        return "Tuple(" + repr(self.types) +")"

    def get_dict(self):
        return {i:j for i,j in list(self.dict.items())+list(super.get_dict(self).items())} 


class TList(TTuple):
    def __repr__(self):
        return "List(" + repr(self.types) +")"
    
class TSet(TTuple):
    def __repr__(self):
        return "Set(" + repr(self.types) +")"
    
class TStr(TTuple):
    def __init__(self): 
        pass
    
    def __repr__(self):
        return "Str"
    
    def typeset(self):   
        return st(TStr())
         
class TFunc:
    @staticmethod
    def abs(tlist):
        return tlist[0]
    
    @staticmethod
    def max(tlist):
        return TypeSet.union_all(tlist)

    @staticmethod
    def filter(tlist):
        return tlist[1]
    
    @staticmethod
    def next(tlist):
        res = tlist[0].types
        if len(tlist)==0:
            res.update(tlist[1])
        return res
    
    @staticmethod
    def sum(tlist):
        TASSERT(1<=len(tlist)<=2)
        types = set()
        for i in tlist[0]:
            if isinstance(i, TSeq):
                types.update(i.typeset())
        TASSERT(len(types) > 0)
        if (len(tlist)==1):
            tlist.append({INT, FLOAT, COMPLEX})
        res = types.intersection(tlist[1])
        TASSERT(len(res)>0)
        return TypeSet(res)

argfunc = {
           'abs' : TFunc.abs,
           'max' : TFunc.max,
           'min' : TFunc.max,
           'filter' : TFunc.filter,
           'next' : TFunc.next,
           'pow' : TFunc.max,
           'reversed' : TFunc.abs,
           'sorted' : TFunc.abs,
           'sum' : TFunc.sum,
           }

BOOL = TObject(bool)
STR = TStr()
INT, FLOAT, COMPLEX = TInt(), TFloat(), TNum(complex)
NONE = TObject(type(None))

funcres= {
          'all' : BOOL,
          'any' : BOOL,
          'ascii' : STR,
          'bin' : STR,
          'bool' : BOOL,
          'bytes' : TObject(bytes),
          'bytearray' : TObject(bytearray),
          'callable' : BOOL,
          'chr' : STR,
          'complex' : TNum(complex),
          'divmod' : TTuple([st(INT), st(INT)]),
          'dir' : TDict([st(STR)], [st(STR)]),
          'float' : TFloat,
          'frozenset' : TObject(frozenset),
          'globals': TDict([st(STR)], [st(STR)]),
          'hasattr': BOOL,
          'hash': INT,
          'hex': STR,
          'id': INT,
          'input' : STR,
          'int' : INT,
          'isinstance' : BOOL,
          'issubclass' : BOOL,
          'iter' : TIter(Bottom),
          'len' : INT,
          'list' : TList([]),
          'locals' : TDict([st(STR)], [st(Any)]),
          'map' : TSeq(Any),
          'memoryview': TObject(memoryview),
          'object' : TObject(object),
          'oct' : STR,
          'ord' : INT,
          'print' : NONE,
          'range' : TIter(INT),
          'repr' : STR,
          'round' : INT,
          'set' : TSet,
          'setattr' : NONE,
          'slice' : slice,
          'str' : STR,
          'tuple' : TTuple( [] ),
          'type' : TObject(type),
          'vars' : TDict([st(STR)], [st(STR)]),
          
          }