
'''
the Composite design-pattern

Component
* is the abstraction for all components, including composite ones
* declares the interface for objects in the composition
* (optional) defines an interface for accessing a component's parent in the recursive structure, and implements it if that's appropriate
Leaf
* represents leaf objects in the composition .
* implements all Component methods
Composite
* represents a composite Component (component having children)
* implements methods to manipulate children
* implements all Component methods, generally by delegating them to its children

here:
Component = InstanceInterface
Leaf = Instance
Compsite = TypeSet

'''

class InstanceInterface:
    ''' Component
    * is the abstraction for all components, including composite ones
    * declares the interface for objects in the composition
    * (optional) defines an interface for accessing a component's parent in the recursive structure, and implements it if that's appropriate
    '''
    def __init__(self):
        pass
    
    def call(self, args:list):
        raise NotImplementedError()
    
    def lookup(self, name:str):
        raise NotImplementedError()
    
    def bind(self, obj):
        return self      
  
    def get_unspecific(self):
        return self

    def bind_parameter(self, param):
        return self
    
class AnyType(InstanceInterface):
    def __repr__(self):
        return "Any"
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{ANY}] * n
    
    def call(self, args):
        return self
    
    def lookup(self, name):
        return self

    def tostr(self):
        return 'Any'

ANY = AnyType()
 
'''
join(specificA, specificA)==instance(A)
join(typeset, instance)==typeset+instance
join(instance1, instance2)==typeset([instance1, instance2])
join(any, *)==any 
'''

'transition function'
def join(a, b):
    if b is None:               return a
    if a == b:                  return a
    if a is ANY or b is ANY:    return ANY

    if type(a.get_unspecific())==type(b.get_unspecific()) and type(a)==Specific:
        return a.get_unspecific()

    if type(a) == type(b) == Instance:
        return TypeSet([a, b])
    
    return a + b
 
'''
type set
'''

def st(t):
    return TypeSet({t})

def nts():
    return TypeSet({})

def joinall(iterable):
    from functools import reduce
    return reduce(join, iterable, nts())

class TypeSet(InstanceInterface):
    '''Composite
    * represents a composite Component (component having children)
    * implements methods to manipulate children
    * implements all Component methods, generally by delegating them to its children
    '''
    def __init__(self, instances):
        self.types = set(instances)
    
    def call(self, args:list):
        return joinall(t.call(args) for t in self.types)
    
    def lookup(self, name:str):
        return joinall(t.lookup(name) for t in self.types)

    def readjust(self, other):
        self.types = other.types

    def bind(self, name, value):
        for t in self.types:
            t.bind(name, value) 

    def add(self, obj):
        if type(obj) == TypeSet:
            self.types.update(obj.types)
        else:
            self.types.add(obj)
    
    def __add__(self, obj):
        'not mutating'
        res = TypeSet(self.types)
        res.add(obj)
        if len(res.types) == 1:
            return res.types.pop()
        return res
    
    __radd__ = __add__
    
    def __bool__(self):
        return len(self.types) > 0

    def tostr(self):
        return 'T{0}'.format(', '.join([t.tostr() for t in self.types]))
    
from symtable import SymTable
    
class Instance(InstanceInterface):
    '''
    existance justified by the fact that "self.x=5" changes interface, just like a.x=5
    '''
    def __init__(self, mytype:InstanceInterface=None, sym:SymTable=None):
        if sym is None:
            sym = SymTable()
        
        self.mytype = mytype
        self.sym = sym
        
    def call(self, args):
        return self.lookup('__call__').call(args)
    
    def lookup(self, name):
        return join(self.sym[name], self.mytype.lookup(name).bind_parameter(self))
    
    def tostr(self):
        return self.get_type().name
    
    def get_type(self):
        return self.mytype
    
    def bind(self, name, value):
        self.sym.bind(name, value) 

    
class Specific(Instance):
    def __init__(self, mytype, value):
        '@value is THE ONLY place where source object is in the target type-system'
        Instance.__init__(self, mytype)
        self.value = value

    def get_unspecific(self):
        return self.get_type().instance

    def lookup(self, name:str):
        return self.get_unspecific().lookup(self, name)

    def bind(self, obj):
        return Instance.bind(self, obj)

    def tostr(self):
        return self.get_unspecific().tostr() + '[{0}]'.format(self.value)
    
TYPECONT = [None]
    
class Class(Instance):
    def __init__(self, name:str, sym:SymTable=None):
        if sym is None: sym = SymTable()
        assert type(name) is str and type(sym) is SymTable
        sym.bind(name, self)
        self.name = name
        Instance.__init__(self, TYPECONT[0], sym)
        self.instance = Instance(self)
        
    def call(self, args):
        init = self.lookup('__init__')
        if not init or init.bind_parameter(self.instance).call(args):
            return self.instance
        return nts()
    
    def lookup(self, name):
        return join(self.sym[name], self.mytype.lookup(name).bind_parameter(self))
    
    def tostr(self):
        return self.get_type().name + '<{0}>'.format(self.name) 
# #
'''
Specific Type Objects
'''
# # 

class Type(Class):
    def __init__(self):
        TYPECONT[0] = self
        Class.__init__(self, 'type', SymTable())
        
    def tostr(self):
        return 'type'

    def lookup(self, name):
        return self.sym[name]
  
TYPE = Type()

BOOL = Class('bool')
INT = Class('int')
FLOAT = Class('float')
COMPLEX = Class('complex')

NONE = Specific(Class('NoneType'), None)

BYTES = STR = TUPLE = LIST = SEQ = DICT = ANY

 
if __name__ == '__main__':
    import analyze
    analyze.main()        
