class int:
    def __neg__(self):
        return 0
    def __repr__(self):
        return ''
    def __pos__(self):
        return 0
    def __int__(self):
        return 0
    def __truediv__(self, y):
        return 0.0
    def __abs__(self):
        return 0
    def __str__(self):
        return ''
    def __bool__(self):
        return False
    
    def bit_length(self):
        return 0
    
    def __rlshift__(self, y):
        return 0
    def __rshift__(self, y):
        return 0
    def __rrshift__(self, y):
        return 0
    def __and__(self, y):
        return 0
    def __rand__(self, y):
        return 0
    def __add__(self, y):
        return 0
    def __xor__(self, y):
        return 0
    def __radd__(self, y):
        return 0
    def __rxor__(self, y):
        return 0
    def __sub__(self, y):
        return 0
    def __or__(self, y):
        return 0
    def __rsub__(self, y):
        return 0
    def __ror__(self, y):
        return 0
    def __mul__(self, y):
        return 0
    def __rmul__(self, y):
        return 0
    def __float__(self):
        return 0.0
    def __mod__(self, y):
        return 0
    def __floordiv__(self, y):
        return 0
    def __rmod__(self, y):
        return 0
    def __rfloordiv__(self, y):
        return 0
    def __pow__(self, y, z=0):
        return 0
    def __rpow__(self, x, z=0):
        return 0
#x[y:z] <==> x[y.__index__():z.__index__()] ??


    def from_bytes(self, bytes, byteorder, *, signed=False):
        return 0