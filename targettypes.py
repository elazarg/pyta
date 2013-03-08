
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
    
    def bind_lookups(self, name:str):
        raise NotImplementedError()
  
    def filter(self, func):
        if func(self):
            return self
        return EMPTY()
      
    def bind(self, obj):
        return self      
  
    def get_unspecific(self):
        return self

    def bind_parameter(self, param):
        return self
    
class AnyType(InstanceInterface):
    def __repr__(self):
        return "Any"
    
    def filter(self, func):
        return self
    
    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [{ANY}] * n
    
    def call(self, args):
        return self
    
    def bind_lookups(self, name):
        return self

    def tostr(self):
        return 'Any'

ANY = AnyType()
 
'''
meet(specificA, specificA)==instance(A)
meet(typeset, instance)==typeset+instance
meet(instance1, instance2)==typeset([instance1, instance2])
meet(any, *)==any 
'''

'transition function'
def meet(a, b):
    if b == EMPTY():              return a
    if a == EMPTY():              return b
    if a == b:                  return a
    if a is ANY or b is ANY:    return ANY
    
    if (type(a.get_unspecific()) == type(b.get_unspecific()) and
         (type(a) == Specific or type(b) == Specific)):
        return a.get_unspecific()

    if issubclass(type(a), Instance) and issubclass(type(b), Instance):
        return TypeSet([a, b])
    
    res = a + b
    return res
 
'''
type set
'''
def EMPTY():
    return TypeSet({})

def meetall(iterable):
    from functools import reduce
    return reduce(meet, iterable, EMPTY())

class TypeSet(InstanceInterface):
    '''Composite
    * represents a composite Component (component having children)
    * implements methods to manipulate children
    * implements all Component methods, generally by delegating them to its children
    '''
    def __init__(self, instances):
        self.types = set(instances)
    
    def call(self, args:list):
        return meetall(t.call(args) for t in self.types)
    
    def bind_lookups(self, name:str):
        return meetall(t.bind_lookups(name) for t in self.types)
    '''
    def readjust(self, other):
        self.types = other.types
    '''
    def bind(self, name, value):
        return meetall(t.bind(name, value) for t in self.types)

    def get_meet_all(self):
        return meetall(t.get_meet_all() for t in self.types if isinstance(t, Seq))
    
    def filter(self, func):
        return TypeSet(t for t in self.types)

    def add(self, obj):
        if type(obj) == TypeSet:
            for i in obj.types:
                self.add(i)
        else:
            others = set()
            while len(self.types) > 0:
                s = self.types.pop()
                res = meet(s, obj)
                if not isinstance(res, TypeSet):
                    self.types.add(res)
                    self.types.update(others)
                    return
                others.add(s)
            self.types.update(others.union({obj}))
            
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

    def isempty(self):
        return len(self.types) > 0
    
    def __eq__(self, other):
        if isinstance(other, TypeSet):
            return self.types == other.types
        else:    
            return len(self.types) == 1 and {other} == self.types
        
    def tostr(self):
        if self:
            return 'T{' + '{0}'.format(', '.join([t.tostr() for t in self.types])) + '}'
        else:
            return '-'
    

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
        return self.bind_lookups('__call__').call(args)
    
    def bind_lookups(self, name):
        return meet(self.sym[name], self.mytype.bind_lookups(name).bind_parameter(self))
    
    def tostr(self):
        return self.mytype.name
    
    def get_type(self):
        return self.mytype
    
    def bind(self, name, value):
        self.sym.bind_type(name, value) 

    
class Specific(Instance):
    pool = {}
    def __init__(self, mytype, value):
        '@value is THE ONLY place where source object is in the target type-system'
        Instance.__init__(self, mytype)
        self.value = value
        Specific.pool[(mytype, value)] = self
         
    @staticmethod
    def factory(mytype, value):
        if (mytype, value) in Specific.pool:
            return Specific.pool[(mytype, value)]
        return Specific(mytype, value)
                
    def get_unspecific(self):
        return self.get_type().instance

    def bind_lookups(self, name:str):
        return self.get_unspecific().bind_lookups(name)

    def bind(self, obj):
        return Instance.bind(self, obj)

    def tostr(self):
        return self.get_unspecific().tostr() + '[{0}]'.format(self.value)
    
    def __repr__(self):
        return self.tostr()

TYPECONT = [None]

class Class(Instance):
    def __init__(self, name:str, sym=None):
        if sym is None: sym = SymTable()
        assert type(name) is str and type(sym) is SymTable
        self.name = name
        Instance.__init__(self, TYPECONT[0], sym)
        self.instance = Instance(self)
        
    def call(self, args):
        init = self.bind_lookups('__init__')
        if not init:
            if len(args.args)==0:
                return self.instance
            return EMPTY()
        if init.bind_parameter(self.instance).call(args):
            return self.instance
        return EMPTY() 
    
    def bind_lookups(self, name):
        return meet(self.sym[name], self.mytype.bind_lookups(name).bind_parameter(self))
    
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
        self.instance = Class('@generic')
        self.instance.instance = None
        
    def tostr(self):
        return 'type'

    def bind_lookups(self, name):
        return self.sym[name]
  
TYPE = Type()

INT = Class('int')
FLOAT = Class('float')
COMPLEX = Class('complex')

BOOL = Class('bool')

TRUE = Specific.factory(BOOL, True)
FALSE = Specific.factory(BOOL, False)
NONE = Specific.factory(Class('NoneType'), None)

BYTES = SEQ = DICT = ANY

TUPLE = Class('tuple')
LIST = Class('list')
STR = Class('str')

class Seq(Instance):
    def __init__(self, targs):
        self.instance_vars = SymTable()
        super().__init__(TypeSet(targs))
    
    def split_to(self, n):
        'should it be a copy?'
        return [self.mytype] * n
    
    def get_meet_all(self):
        return self.mytype
        
    def __repr__(self):
        return "Seq(" + repr(self.mytype) + ")"

    # def get_dict(self):       return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())} 


class Iter(Seq):
    def __repr__(self):
        return "Iter(" + repr(self.types) + ")"

class Dict(Seq):
    def __init__(self, tkeys, tvalues):
        from itertools import product
        self.instance_vars = SymTable()   
        skeys = TypeSet.union_all(tkeys) if len(tkeys) != 0 else TypeSet({})
        temp = set(sum([list(product(k, v)) for k, v in zip(tkeys, tvalues)], []))
        self.types = { k : TypeSet([v for tk, v in temp if tk == k]) for k in skeys}
    
    def __repr__(self):
        return "Dict(" + repr(self.types) + ")"

class Tuple(Seq):
    def __init__(self, tvalues):
        self.tupletypes = tuple(tvalues)
        super().__init__(self.tupletypes)
        self.type = TUPLE
            
    def tostr(self):
        return repr(self.tupletypes)
    
    def __len__(self):
        return len(self.tupletypes)
 
    def split_to(self, n):
        if len(self.tupletypes) == n:
            return self.tupletypes
        else:
            return tuple([TypeSet() for _ in range(n)])  
 
    def __repr__(self):
        return repr(self.tupletypes)

    def __eq__(self, other):
        return type(self) is type(other) and self.tupletypes == other.tupletypes
    
    def __hash__(self):
        return hash(self.tupletypes)
    
class Str(Tuple):
    def __init__(self, string):
        self.tvalues = string
        self.settypes = tuple(Specific.factory(STR, c) for c in string)
        super().__init__(self.settypes)
        self.type = STR
    
    def __repr__(self):
        return repr(self.tvalues)

    def __eq__(self, other):
        return type(other) is Str and self.tvalues == other.tvalues
    
    def __hash__(self):
        return hash(self.settypes)
        
    def tostr(self):
        return repr(self.tvalues)
    
class List(Tuple):
    def __init__(self, tvalues):
        self.tupletypes = list(tvalues)
        super().__init__(self.tupletypes)
        self.tupletypes = list(tvalues)
        self.type = List
            
    def tostr(self):
        return repr(self.tupletypes)
 
    def __repr__(self):
        return repr(self.tupletypes)
