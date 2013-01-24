'''
    def __repr__(self):
        return repr(x)
    def __getattribute__('name'):
        return x.name
    def __ne__(self, y):
        return x!=y
    def __lt__(self, y):
        return x<y
    def __le__(self, y):
        return x<=y
    def __eq__(self, y):
        return x==y
    def __getitem__(self, y):
        return x[y]
    def __sizeof__(self) -- size of L in memory, in bytes
    def __gt__(self, y):
        return x>y
'''

#TODO : Handle mutators
class tuple:
#    def __iter__(self):        return iter(x)
#    def __reversed__(self):    return Reversed()
    def __init__(self, *args):
        return None
    def count(self, value):
        return 0
    def __len__(self):
        return 0
    def index(self, value, start=0, stop=1000):
        return 0
    def __add__(self, y):
        return self
    def __mul__(self, n):
        return self
    def __rmul__(self, n):
        return self
    def __contains__(self, y):
        return False
    def __iadd__(self, y):
        return self
    def __imul__(self, y):
        return self

    
#TODO : Handle mutators
class list:
    def clear(self):
        return None
    def copy(self):
        return self
#    def __iter__(self):        return iter(x)
#    def __reversed__(self):    return Reversed()
    def append(self, obj):
        return None
    def __init__(self, *args):
        return self
    def count(self, value):
        return 0
    def insert(self, index, obj):
        return None
    def __len__(self):
        return 0
    def extend(self, iterable):
        return None
    def pop(self, index=1000):
        return self[len()]
    def __setitem__(self, i, y):
        return self
    def remove(self, value):
        return None
    def __delitem__(self, self, y):
        return None
    def index(self, value, start=0, stop=1000):
        return 0
    def __add__(self, y):
        return self
    def reverse(self, self):
        return None
    def __mul__(self, n):
        return self
    def sort(self, key=None, reverse=False):
        return None
    def __rmul__(self, n):
        return self
    def __contains__(self, y):
        return False
    def __iadd__(self, y):
        return self
    def __imul__(self, y):
        return self
        