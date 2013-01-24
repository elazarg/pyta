'''
Returns self, the complex conjugate of any int.
x.__getattribute__('name') <==> x.name
int.bit_length() -> int

Number of bits necessary to represent self in binary.
>>> bin(37)
'0b100101'
>>> (37).bit_length()
6
x.__lt__(y) <==> x<y
x.__lshift__(y) <==> x<<y
x.__invert__() <==> ~x
x.__le__(y) <==> x<=y
int.from_bytes(bytes, byteorder, *, signed=False) -> int

x.__rlshift__(y) <==> y<<x
x.__eq__(y) <==> x==y
x.__rshift__(y) <==> x>>y
Flooring an Integral returns itself.
x.__ne__(y) <==> x!=y
x.__rrshift__(y) <==> y>>x
Ceiling of an Integral returns itself.
x.__gt__(y) <==> x>y
x.__and__(y) <==> x&y
Rounding an Integral returns itself.
Rounding with an ndigits argument also returns an integer.
x.__ge__(y) <==> x>=y
x.__rand__(y) <==> y&x
None
x.__add__(y) <==> x+y
x.__xor__(y) <==> x^y
None
x.__radd__(y) <==> y+x
x.__rxor__(y) <==> y^x
Returns size in memory, in bytes
x.__sub__(y) <==> x-y
x.__or__(y) <==> x|y
the real part of a complex number
T.__new__(S, ...) -> a new object with type S, a subtype of T
x.__rsub__(y) <==> y-x
x.__ror__(y) <==> y|x
x.__mul__(y) <==> x*y
the numerator of a rational number in lowest terms
x.__rmul__(y) <==> y*x
the denominator of a rational number in lowest terms
x.__float__() <==> float(x)
x.__mod__(y) <==> x%y
x.__floordiv__(y) <==> x//y
x.__rmod__(y) <==> y%x
x.__rfloordiv__(y) <==> y//x
int.to_bytes(length, byteorder, *, signed=False) -> bytes

Return an array of bytes representing an integer.

The integer is represented using length bytes.  An OverflowError is
raised if the integer is not representable with the given number of
bytes.

The byteorder argument determines the byte order used to represent the
integer.  If byteorder is 'big', the most significant byte is at the
beginning of the byte array.  If byteorder is 'little', the most
significant byte is at the end of the byte array.  To request the native
byte order of the host system, use `sys.byteorder' as the byte order value.

The signed keyword-only argument determines whether two's complement is
used to represent the integer.  If signed is False and a negative integer
is given, an OverflowError is raised.
x.__divmod__(y) <==> divmod(x, y)
the imaginary part of a complex number
x.__rdivmod__(y) <==> divmod(y, x)
x.__rtruediv__(y) <==> y/x
str(object[, encoding[, errors]]) -> str

Create a new string object from the given object. If encoding or
errors is specified, then the object must expose a data buffer
that will be decoded using the given encoding and error handler.
Otherwise, returns the result of object.__str__() (if defined)
or repr(object).
encoding defaults to sys.getdefaultencoding().
errors defaults to 'strict'.
x.__pow__(y[, z]) <==> pow(x, y[, z])
x[y:z] <==> x[y.__index__():z.__index__()]
y.__rpow__(x[, z]) <==> pow(x, y[, z])
Truncating an Integral returns itself.
'''

class int:
    def __neg__(self):
        return 0
    def __repr__(self):
        return ''
    def __pos__(self):
        return 0
    def __int__(self):
        return 0
    def __hash__(self):
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