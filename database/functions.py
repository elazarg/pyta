
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

def callable(obj):
    return False

def chr(st):
    return ""


def divmod(x,y):
    return (0,0)

def dir(obj):
    return {"":""}

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

def bin(obj):
    return ""
def isinstance(obj, t):
    return False

def issubclass(obj):
    return False

def len(obj):
    return 0


def locals():
    return {"" : ""}

def oct(num):
    return ""

def ord(st):
    return 0

def print(*x, sep=' ', end='\n'):
    return None

def repr(obj):
    return ""

def round(obj):
    pass
    return 0



def setattr():
    return None
'''
def bool(obj=0):
    return False

def bytes(obj=b''):
    return b''


def complex(x=0):
    return 0j

def float(obj=0.0):
    return 0.0

def int(obj=0):
    return 0

def list(obj):
    return []
def set():
    return {}
def str():
    return ""
def tuple():
    return ()
def type(x):
    class type:
        pass
    return type


'''
def vars():
    return {"" : ""}

def pow(x,y,z=0):
    return x

def abs(x):
    return x

def max(a,b): 
    return a

def min(a, b):
    return a

def filter():
    return []

def next(x):
    return x.__next__()
    
def reversed():
    return []

def sorted():
    return []
    
def sum(iterable):
    return iterable[0]

def map(func, *iterables):
    return iterables
