from symtable import SymTable

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
    

class Specific(Instance):
    def get_unspecific(self):
        raise NotImplementedError

TYPE=None

class Class(Instance):
    def __init__(self):
        Instance.__init__(self, TYPE)
        
    def call(self, args):
        if self.lookup('__init__').ismatch(args):
            return self.instance
        return st({})
    
    def lookup(self, name):
        return self.sym[name].union(self.mytype.lookup(name).bind(self))
 
##
'''
Specific Type Objects
'''
##

class Type(Class):
    def __init__(self):
        global TYPE
        TYPE=self
        Instance.__init__(self, self)

class AnyType(InstanceInterface):
    def __repr__(self):
        return "Any"
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{Any}] * n
    
    def call(self, args):
        return self
    
    def lookup(self, name):
        return self
    

Any = AnyType()

'''
type set
'''

def invariant(m):
    def wrapped(self, *args, **keyargs):
        res = m(self, *args, **keyargs)
        self.to_invariant()
        return res
    return wrapped

def st(t):
    return TypeSet({t})

def nts():
    return TypeSet({})

class TypeSet(InstanceInterface):    
    @invariant
    def __init__(self, instances):
        self.types = set(instances)
    
    def call(self, args:list):
        return join(t.call(args) for t in self.types)
    
    def lookup(self, name:str):
        return join(t.lookup(name) for t in self.types)
        
    @invariant
    def readjust(self, other):
        self.types = other.types
    
    @invariant
    def add(self, obj):
        if type(obj)==TypeSet:
            self.types.update(obj.types)
        else:
            self.types.add(obj)

'''
join(specificA, specificA)==instance(A)
join(typeset, instance)==typeset+instance
join(instance1, instance2)==typeset([instance1, instance2])
join(any, *)==any 
'''

'transition function'
def join(a:InstanceInterface, b:InstanceInterface):
    if a==b:                    return a
    if a is Any or b is Any:    return Any
    
    if type(a.get_unspecific())==type(b.get_unspecific())==Specific:
        return a.get_unspecific()
    if type(a)==type(b)==Instance:
        return TypeSet([a, b])
      
    if type(a)==TypeSet:
        return a.add(b)
    return b.add(a)
        