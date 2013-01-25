from typeset import TypeSet, st, TObject
from itertools import product
from definitions import TFunc

class TNum(TObject):
    def __init__(self, t):
        self.dict = {}
        self.t = t
    
    def get_dict(self):
        return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())}

    def __repr__(self):
        return "num"

    def new_instance(self):
        return TObject(TNum, self.t)     

class TInt(TNum):
    def __init__(self, t=int):
        self.dict = {}
        self.t=t
    
    def __repr__(self):
        return "int"


class TBool(TNum):
    def __init__(self, t=bool):
        self.dict = TInt().dict
        self.t=bool

    def __repr__(self):
        return "bool"

class TFloat(TNum):
    def __init__(self, t=float):
        self.dict = TInt().dict
        self.t=bool    
    
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
        self.additems()
    
    def additems(self):
        import ast
        args = ast.arguments([ast.arg('x', None)], None, None, [], None, None, [], [])
        def getitem(actual_args):
            if not all(hasattr(x, 'value') for x in actual_args.args[0]):
                return self.typeset()
            values = [x.value for x in actual_args.args[0] if isinstance(x.value, int)]
            return TypeSet(self.types[v] for v in values if v < len(self.types))
        func = TFunc(args, getitem , 'attr')
        self.dict.update({'__getitem__' : st(func) }) 
        
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
        self.dict = {}
        self.t = t
    
    def __repr__(self):
        return repr(self.t).split("'")[1]
    
    def typeset(self):   
        return st(TStr())

    

STR = TStr(str)
BYTES = TStr(bytes)
INT, FLOAT, COMPLEX = TInt(), TFloat(), TNum(complex)
