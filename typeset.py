
def st(t):
    return TypeSet({t})

class TObject:
    def __init__(self, s=None, t=None):
        if t == None and s != None:
            t = type(s)
        self.type = t
        self.super = s
        self.dict = {}

    def __repr__(self):
        return repr(self.type).split(sep="'")[1]
    '''
    def __eq__(self, other):
        return self.t == other.t
    ''' 
    def has_type_attr(self, attr):
        res = self.get_type_attr(attr)
        return res != None
        
    def get_type_attr(self, attr):
        res = self.dict.get(attr)
        if res == None:
            res = self.type.get_type_attr(attr)
            res = TypeSet({a.with_bind(self) for a in res})
        return res

    def ismatch(self, actual_args):
        return False
    
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


class TypeSet:
    def invariant(m):
        def wrapped(self, *args):
            res = m(self, *args)
            self.to_invariant()
            return res
        return wrapped
    
    @invariant
    def __init__(self, iterable):
        assert not isinstance(iterable, TypeSet)
        self.types = set(iterable)
    
    @invariant
    def readjust(self, other):
        self.types = other.types
    
    @invariant
    def update(self, iterable):
        self.types.update(iterable)
        
    @invariant
    def add(self, obj):
        assert not isinstance(obj, TypeSet)
        self.types.add(obj)

    @invariant
    def union(self, other):
        assert isinstance(other, TypeSet)
        return TypeSet(set.union(self.types, other.types)) 
    
    def to_invariant(self):
        assert not isinstance(self.types, TypeSet)
        assert not any(isinstance(i, TypeSet) for i in self.types)
        if not all(issubclass(type(t), TObject) for t in self.types):
            print(self.types)
            assert False
        if Any in self.types:
            self.types = {Any}
    
    def __iter__(self):
        return self.types.__iter__()
    
    @staticmethod
    def union_all(iterable):
        if len(iterable)==0:
            return TypeSet({})
        return TypeSet(set.union(*[i.types for i in iterable]))
    
    def __repr__(self):
        return 'T{' +', '.join([str(i) for i in self.types]) +'}'
    '''
    def __str__(self):
        return 'TypeSet {0}'.format({type(i) for i in self.types})
    '''     
    def __len__(self):
        return len(self.types)
 
Empty = TypeSet({})
