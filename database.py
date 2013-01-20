from itertools import product
from functools import reduce

def TASSERT(b): 
    if not b:
        print('ERROR')

class AnyClass:
    def __repr__(self):
        return "<class 'Any'>"
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{Any}] * n

Any = AnyClass()

class TypeSet:
    def __init__(self, iterable):
        self.types = set(iterable)
        self.to_invariant()
        
    def update(self, iterable):
        self.types.update(iterable)
        self.to_invariant()
        
    def add(self, obj):
        self.types.add(obj)
        self.to_invariant()
    
    def to_invariant(self):
        if Any in self.types:
            self.types = {Any}
    
    def __iter__(self):
        return self.types.__iter__()
    
    @staticmethod
    def union_all(iterable):
        return TypeSet(reduce(set.union, [i.types for i in iterable]))
    
    def __repr__(self):
        return repr(self.types)

class Bottom:
    def __repr__(self):
        return "<class 'Bottom'>"


class TSeq:
    def __init__(self, *targs):
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
        return "<class 'TSeq(" + repr(self.types) +")'>"

class TIter(TSeq):
    def __repr__(self):
        return "<class 'TIter(" + repr(self.types) +")'>"

class TDict(TSeq):
    def __init__(self, tkeys, tvalues):
        skeys = TypeSet.union_all(tkeys)
        temp = set(sum([list(product(k,v)) for k,v in zip(tkeys, tvalues)], []))
        self.types = { k : TypeSet([v for tk, v in temp if tk==k]) for k in skeys}
    
    def __repr__(self):
        return "<class 'TDict(" + repr(self.types) +")'>"

class TTuple(TSeq):
    def __init__(self, tvalues):
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
        return "<class 'TTuple(" + repr(self.types) +")'>"

class TList(TTuple):
    def __repr__(self):
        return "<class 'TList(" + repr(self.types) +")'>"

class TFunc:
    @staticmethod
    def abs(tlist):
        return tlist[0]
    
    @staticmethod
    def max(tlist):
        s=set()
        for i in tlist:
            s.update(i)
        return i

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
            tlist.append({int, float, complex})
        res = types.intersection(tlist[1])
        TASSERT(len(res)>0)
        return res

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

funcres= {
          'all' : bool,
          'any' : bool,
          'ascii' : str,
          'bin' : str,
          'bool' : bool,
          'bytes' : bytes,
          'bytearray' : bytearray,
          'callable' : bool,
          'chr' : str,
          'complex' : complex,
          'divmod' : TTuple([int, int]),
          'float' : float,
          'frozenset' : frozenset,
          'globals': dict,
          'hasattr': bool,
          'hash': int,
          'hex': str,
          'id': int,
          'input' : str,
          'int' : int,
          'isinstance' : bool,
          'issubclass' : bool,
          'iter' : TIter(Bottom),
          'len' : int,
          'list' : TList([]),
          'locals' : TDict([TypeSet({str})], [TypeSet({Any})]),
          'map' : TSeq(Any),
          'memoryview': memoryview,
          'object' : object,
          'oct' : str,
          'ord' : int,
          'print' : type(None),
          'range' : TIter(int),
          'repr' : str,
          'round' : int,
          'set' : set,
          'setattr' : type(None),
          'slice' : slice,
          'str' : str,
          'tuple' : TTuple( [] ),
          'type' : type,
          'vars' : dict,
          
          }