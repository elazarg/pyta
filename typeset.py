
def st(t):
    return TypeSet({t})

def nts():
    return TypeSet({})

    
class AnyClass():
    def __init__(self):
        super(type)
        
    def __repr__(self):
        return "Any"
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{Any}] * n

Any = AnyClass()


def invariant(m):
    def wrapped(self, *args, **keyargs):
        res = m(self, *args, **keyargs)
        self.to_invariant()
        return res
    return wrapped

class TypeSet:    
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
        '''
        if not all(issubclass(type(t), TObject) for t in self.types):
            print(self.types)
            assert False
        '''
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

