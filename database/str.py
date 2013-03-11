'''
    def endswith(suffix[, start[, end]]):
        return bool
    def __le__(self, y):
        return x<=y
    def __new__(S, ...):
        return a new object with type S, a subtype of T
    def rsplit(sep=None, maxsplit=-1):
        return list of strings
    def islower(self):
        return bool
    def __eq__(self, y):
        return x==y
    def join(iterable):
        return str
    def isupper(self):
        return bool
str(object[, encoding[, errors]]):
        return str
    def __ne__(self, y):
        return x!=y
    def capitalize(self):
        return str
    def istitle(self):
        return bool
    def casefold(self):
        return str
    def isspace(self):
        return bool
    def title(self):
        return str
    def __ge__(self, y):
        return x>=y
    def isdecimal(self):
        return bool
    def rstrip([chars]):
        return str
    def center(width[, fillchar]):
        return str
    def __iter__(self):
        return iter(x)
    def isdigit(self):
        return bool
    def encode(encoding='utf-8', errors='strict'):
        return bytes
    def count(sub[, start[, end]]):
        return int
    def __mod__(self, y):
        return x%y
    def isnumeric(self):
        return bool
    def expandtabs([tabsize]):
        return str
    def isalpha(self):
        return bool
    def find(sub[, start[, end]]):
        return int
    def isalnum(self):
        return bool
    def partition(sep):
        return (head, sep, tail)
    def translate(table):
        return str
    def isidentifier(self):
        return bool
    def __getitem__(self, y):
        return x[y]
    def index(sub[, start[, end]]):
        return int
    def isprintable(self):
        return bool
    def __add__(self, y):
        return x+y
    def ljust(width[, fillchar]):
        return str
    def zfill(width):
        return str
    def __mul__(n):
        return x*n
    def lower(self):
        return str
    def format(*args, **kwargs):
        return str
    def __len__(self):
        return len(x)
    def lstrip([chars]):
        return str
    def format_map(mapping):
        return str
    def rfind(sub[, start[, end]]):
        return int
    def __format__(format_spec):
        return str
    def rindex(sub[, start[, end]]):
        return int
    def __getattribute__('name'):
        return x.name
    def __sizeof__(self):
        return size of S in memory, in bytes
    def rjust(width[, fillchar]):
        return str
    def __rmul__(n):
        return n*x
    def rpartition(sep):
        return (head, sep, tail)
    def __rmod__(self, y):
        return y%x
    def splitlines([keepends]):
        return list of strings
    def __repr__(self):
        return repr(x)
    def strip([chars]):
        return str
    def __hash__(self):
        return hash(x)
    def swapcase(self):
        return str
    def __contains__(self, y):
        return y in x
    def __str__(self):
        return str(x)
    def replace(old, new[, count]):
        return str
    def upper(self):
        return str
    def __gt__(self, y):
        return x>y
    def split(sep=None, maxsplit=-1):
        return list of strings
    def startswith(prefix[, start[, end]]):
        return bool
    def __lt__(self, y):
        return x<y

str(object[, encoding[, errors]]):
        return str
'''
    
class str:
    def endswith(self, suffix, start=0, end=1000):
        return False
    def rsplit(self, sep=None, maxsplit=-1):
        return ['']
    def islower(self):
        return False
    def join(self, iterable):
        return ''
    def isupper(self):
        return False
    def capitalize(self):
        return ''
    def istitle(self):
        return False
    def casefold(self):
        return ''
    def isspace(self):
        return False
    def title(self):
        return ''
    def isdecimal(self):
        return False
    def rstrip(self, chars):
        return ''
    def center(self, width, fillchar=''):
        return ''
#    def __iter__(self):    return iter()
    def isdigit(self):
        return False
    def encode(self, encoding='utf-8', errors='strict'):
        return b''
    def count(self, sub, star=0, end=1000):
        return 0
    def __mod__(self, y):
        return ''
    def isnumeric(self):
        return False
    def expandtabs(self, tabsize=8):
        return ''
    def isalpha(self):
        return False
    def find(self, sub, start=0, end=1000):
        return 0
    def isalnum(self):
        return False
    def partition(self, sep):
        return ('', '', '')
    def translate(self, table):
        return ''
    def isidentifier(self):
        return False
    def __getitem__(self, y):
        return ''
    def index(self, sub, start=0, end=1000):
        return 0
    def isprintable(self):
        return False
    def __add__(self, y):
        return ''
    def ljust(self, width, fillchar=''):
        return ''
    def zfill(self, width):
        return str
    def __mul__(self, n):
        return ''
    def lower(self):
        return ''
    def format(self, *args, **kwargs):
        return ''
    def __len__(self):
        return 0
    def lstrip(self, chars=''):
        return ''
    def format_map(self, mapping):
        return ''
    def rfind(self, sub, start=0, end=1000):
        return 0
    def __format__(self, format_spec):
        return ''
    def rindex(self, sub, start=0, end=1000):
        return 0
    def __sizeof__(self):
        return 0
    def rjust(self, width, fillchar=''):
        return ''
    def __rmul__(self, n):
        return ''
    def rpartition(self, sep):
        return ('', '', '')
    def __rmod__(self, y):
        return y
    def splitlines(self, keepends=True):
        return ['']
    def strip(self, chars):
        return ''
    def swapcase(self):
        return ''
    def __contains__(self, y):
        return False
    def replace(self, old, new, count=0):
        return ''
    def upper(self):
        return ''
    def split(self, sep=None, maxsplit=0):
        return ['']
    def startswith(self, prefix, start=0, end=1000):
        return False
        