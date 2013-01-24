
def st(t):
    return TypeSet({t})

class TObject:
    def __init__(self, t=object):
        self.type = t
        self.dict = {}

    def __repr__(self):
        return repr(self.type).split(sep="'")[1]


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

    def union(self, other):
        assert isinstance(other, TypeSet)
        return TypeSet(set.union(self.types, other.types)) 
    
    def to_invariant(self):
        assert not isinstance(self.types, TypeSet)
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

    def __len__(self):
        return len(self.types)
 
Empty = TypeSet({})
