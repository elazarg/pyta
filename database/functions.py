
#def bytearray(): TObject(bytearray),
#def frozenset(): TObject(frozenset),
#def memoryview(): TObject(memoryview),
#def object(): TObject(object),
#def range(): TIter(INT),
#def slice(): slice,
#def iter():\nTIter(Bottom),

def all():
    return False

def any():
    return False

def ascii():
    return ""

def bin():
    return ""

def bool():
    return False

def bytes():
    return b''

def callable():
    return False

def chr():
    return ""

def complex():
    return 0j

def divmod():
    return (0,0)

def dir():
    return {"":""}

def float():
    return 0.0

def globals():
    return {"":""}

def hasattr():
    return False

def hash():
    return 0

def hex():
    return ""

def id():
    return 0

def input():
    return ""

def int():
    return 0

def isinstance():
    return False

def issubclass():
    return False

def len():
    return 0

def list():
    return []

def locals():
    return {"" : ""}

def map(func, *iterables):
    return iterables

def oct():
    return ""

def ord():
    return 0

def print():
    return None

def repr():
    return ""

def round():
    return 0

def set():
    return {}

def setattr():
    return None

def str():
    return ""

def tuple():
    return ()

def type():
    return type

def vars():
    return {"" : ""}
'''
def abs():  TFunc.abs,
def max():  TFunc.max,
def min():  TFunc.max,
def filter():  TFunc.filter,
def next():  TFunc.next,
def pow():  TFunc.max,
def reversed():  TFunc.abs,
def sorted():  TFunc.abs,
def sum():  TFunc.sum,
'''