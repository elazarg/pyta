
#def bytearray(): TObject(bytearray),
#def frozenset(): TObject(frozenset),
#def memoryview(): TObject(memoryview),
#def object(): TObject(object),
#def range(): TIter(INT),
#def slice(): slice,
#def iter(): TIter(Bottom),

def all(iterable):
    return False

def any(iterable):
    return False

def ascii():
    return ""

def bin(obj):
    return ""

def bool(obj=0):
    return False

def bytes(obj=b''):
    return b''

def callable(obj):
    return False

def chr(st):
    return ""

def complex(x=0):
    return 0j

def divmod(x,y):
    return (0,0)

def dir(obj):
    return {"":""}

def float(obj=0.0):
    return 0.0

def globals():
    return {"":""}

def hasattr(obj, attr):
    return False

def hash(obj):
    return 0

def hex(obj):
    return ""

def id(obj):
    return 0

def input(text=''):
    return ""

def int(obj=0):
    return 0

def isinstance(obj, t):
    return False

def issubclass(obj):
    return False

def len(obj):
    return 0

def list(obj):
    return []

def locals():
    return {"" : ""}

def oct(num):
    return ""

def ord(st):
    return 0

def print(x):
    return None

def repr(obj):
    return ""

def round(obj):
    pass
    return 0

def set():
    return {}

def setattr():
    return None

def str():
    return ""

def tuple():
    return ()

def type(x):
    class type:
        pass
    return type

def vars():
    return {"" : ""}

def pow(x,y,z=0):
    return x

def abs(x):
    return x

'''
def max(a,b):    return a
def min():  TFunc.max,
def filter():  TFunc.filter,
def next():  TFunc.next,
def reversed():  TFunc.abs,
def sorted():  TFunc.abs,
def sum():  TFunc.sum,
def map(func, *iterables):    return iterables
'''