
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
    

ANY = AnyType()
 
'''
join(specificA, specificA)==instance(A)
join(typeset, instance)==typeset+instance
join(instance1, instance2)==typeset([instance1, instance2])
join(any, *)==any 
'''

'transition function'
def join(a, b):
    if a==b:                    return a
    if a is ANY or b is ANY:    return ANY
    '''
    if type(a.get_unspecific())==type(b.get_unspecific())==Specific:
        return a.get_unspecific()
    '''
    if type(a)==type(b)==Instance:
        return TypeSet([a, b])
    
    return a + b
 
'''
type set
'''

def st(t):
    return TypeSet({t})

def nts():
    return TypeSet({})

class TypeSet(InstanceInterface):
    def __init__(self, instances):
        self.types = set(instances)
    
    def call(self, args:list):
        return join(t.call(args) for t in self.types)
    
    def lookup(self, name:str):
        return join(t.lookup(name) for t in self.types)

    def readjust(self, other):
        self.types = other.types

    def add(self, obj):
        if type(obj)==TypeSet:
            self.types.update(obj.types)
        else:
            self.types.add(obj)
    
    def __add__(self, obj):
        'not mutating'
        res = TypeSet(self.types)
        res.add(obj)
        return res
    
    __radd__ = __add__
    
    def __bool__(self):
        return self.types != {}

    def tostr(self):
        return 'T{' + ', '.join([t.tostr() for t in self.types]) + '}'
    
from symtable import SymTable
    
class Instance(InstanceInterface):
    '''
    existance justified by the fact that "self.x=5" changes interface, just like a.x=5
    '''
    def __init__(self, mytype:InstanceInterface=None, sym:SymTable=None):
        if sym is None:
            sym = SymTable()
        
        self.mytype=mytype
        self.sym=sym
        
    def call(self, args):
        return self.lookup('__call__').call(args)
    
    def lookup(self, name):
        return self.sym[name].union(self.mytype.lookup(name).bind(self))
    
    def tostr(self):
        return 'Instance: ' + self.mytype.tostr()
    
    def get_type(self):
        return self.mytype
    
class Specific(Instance):
    def get_unspecific(self):
        raise NotImplementedError

TYPECONT=[None]
    
class Class(Instance):
    def __init__(self, name:str, sym:SymTable=None, cls=None):
        if sym is None: sym=SymTable()
        assert type(name) is str and type(sym) is SymTable
        sym.bind(name, self)
        self.name = name
        Instance.__init__(self, TYPECONT[0], sym)
        
    def call(self, args):
        if self.lookup('__init__').ismatch(args):
            return self.instance
        return st({})
    
    def lookup(self, name):
        return self.sym[name].union(self.mytype.lookup(name).bind(self))
    
    def tostr(self):
        return 'Class: {0}({1})'.format(self.name, self.get_type().tostr()) 
##
'''
Specific Type Objects
'''
##

class Type(Class):
    def __init__(self):
        TYPECONT[0]=self
        Class.__init__(self, 'type', SymTable())
        
    def tostr(self):
        return 'Class: type'

TYPE = Type()


BOOL=Class('bool')
INT=Class('int')
FLOAT=Class('float')
NONE=Class('NoneType')
COMPLEX=Class('complex')

BYTES=STR=TUPLE=LIST=SEQ=DICT=ANY

 
if __name__=='__main__':
    import analyze
    analyze.main()        