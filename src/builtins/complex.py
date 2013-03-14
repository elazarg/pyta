#incomplete
class complex:
    def __neg__(self):
        return 0.0j
    def __pos__(self):
        return 0.0j
    def __int__(self):
        return 0
    def __truediv__(self, y):
        return 0.0j
    def __abs__(self):
        return 0.0
    
    def bit_length(self):
        return 0

    def __add__(self, y):
        return 0.0j
    def __radd__(self, y):
        return 0.0j
    def __sub__(self, y):
        return 0.0j
    def __rsub__(self, y):
        return 0.0j
    def __mul__(self, y):
        return 0.0j
    def __rmul__(self, y):
        return 0.0j
    def __float__(self):
        return 0.0
    def __mod__(self, y):
        return 0.0j
    def __rmod__(self, y):
        return 0.0j
    def __floordiv__(self, y):
        return 0.0j
    def __rfloordiv__(self, y):
        return 0.0j
    def __pow__(self, y, z=0):
        return 0.0j
    def __rpow__(self, x, z=0):
        return 0.0j
#x[y:z] <==> x[y.__index__():z.__index__()] ??

    def from_bytes(self, bytes, byteorder, *, signed=False):
        return 0.0j
    
    def conjugate(self):
        return 0j
    def fromhex(self):
        return 0.0
    def hex(self):
        return ''
    def imag(self):
        return 0j
    def is_integer(self):
        return False
    def real(self):
        return 0.0