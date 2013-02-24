from helpers import Singleton as _Singleton
from symtable import _SymTable as _SymTable
from typeset import _TypeSet as _TypeSet, st as _st
from itertools import product as _product

class TObject:
    '''an object of this class represents some python object of arbitrary type.
    this is not the "object" class for which there will be TObject_Class'''
    def __init__(self, name, sym=None, t=None):
        self.name = name
        if sym==None:
            sym = _SymTable()
        if t==None:
            t = 'object'
        self.sym = sym
        self.t = t
        
    def obj_has_attr(self, attr):
        res = self.obj_get_attr(attr)
        return res != None
    
    def __repr__(self):
        return '{0}, instance of {1}'.format(self.name, self.t)   
    
    def obj_get_attr(self, attr):
        res = self.instance_vars.get_var(attr)
        if res == None:
            if self.s == None:
                'no such instane variable - return class variable'
                res = _TypeSet({a.with_bind(self) for a in self.type.get_type_attr(attr)})
            else:
                #res = self.s.get_type_attr(attr)
                pass
        return res

    def weak_bind(self, var_id, typeset):
        self.sym.bind(var_id, typeset)
    
    def with_bind(self, x):
        '''binds nothing for objects'''
        return self
    
    def get_symtable(self):
        return self.sym


class TObject_Class(TObject):
    '''
    represents the object class
    '''
    __metaclass__ = _Singleton
    def __init__(self, name='object'):        
        super().__init__('Class ' + name)
        
    def new_instance(self, name, sym):
        if sym == None:
            #default parameters are computed only once
            #so mutable objects should not be there
            sym = _SymTable()
        return TObject(name, sym)
    
    def ismatch(self, actual_args):
        return False


class _TNum_Class(TObject_Class):
    def __init__(self, name = 'num'):
        super().__init__(name)
    
    #def get_dict(self):      return {i:j for i, j in list(self.instance_vars.items()) + list(super.get_dict(self).items())}

class _TInt_Class(_TNum_Class):
    def __init__(self, t=int):
        super().__init__('int')

class _TBool_Class(_TNum_Class):
    def __init__(self, t=bool):
        super().__init__('bool')

class _TFloat_Class(_TNum_Class):
    def __init__(self):
        super().__init__('float')

    def new_instance(self, *args):
        return self.instance 

class _TComplex_Class(_TNum_Class):
    def __init__(self):
        super().__init__('complex')

    def new_instance(self, *args):
        return self.instance 

class _TSeq_Class(TObject_Class):
    def __init__(self, *targs):
        super().__init__('seq')
        self.types = set(targs)
    
    def typeset(self):
        return self.types

    def can_split_to(self, n):
        return True
        
    def split_to(self, n):
        return [self.types] * n
    
    def fromset(self, keyset):
        res = self.new_instance(keyset)
        return res
    
    def add(self, t):
        self.types.add(t)
    
    def update(self, tlist):
        self.types.update(tlist)
    
    def __repr__(self):
        return "Seq(" + repr(self.types) + ")"

    #def get_dict(self):       return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())} 


class _TDict_Class(_TSeq_Class):
    def __init__(self, tkeys, tvalues):
        self.instance_vars = _SymTable()   
        skeys = _TypeSet.union_all(tkeys) if len(tkeys) != 0 else _TypeSet({})
        temp = set(sum([list(_product(k, v)) for k, v in zip(tkeys, tvalues)], []))
        self.types = { k : _TypeSet([v for tk, v in temp if tk == k]) for k in skeys}
    
    def __repr__(self):
        return "Dict(" + repr(self.types) + ")"


class TArguments():
    def __init__(self, arg, b = None):         
        rearg = [i.arg for i in arg.args]
        size = len(arg.defaults)
        self.pos = rearg[:-size] if size > 0 else rearg
        
        self.bind = b
        if b != None:
            del self.pos[0]
        
        self.defs = list(zip(rearg[-size:] , arg.defaults))        
        
        self.vararg = arg.vararg
        self.varargannotation = arg.varargannotation
        self.kwonlyargs = [i.arg for i in arg.kwonlyargs]
        self.kwarg = arg.kwarg
        self.kwargannotation = arg.kwargannotation
        self.kw_defaults = arg.kw_defaults
        
        self.names = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  
        
    def with_bind(self, t):
        return TArguments(self.arg, t)
        
    def ismatch(self, actual):
        bind = {}
        bind.update(zip(self.pos, actual.args))
        for keyword in actual.keywords:
            if keyword.arg in bind:
                # double assignment
                print('double assignment: ', keyword.arg)
                return False
            bind[keyword.arg] = keyword.value
        bind.update(self.defs)                        
        leftover = set(self.pos) - set(bind.keys())
        if len(leftover) > 0:
            # positional parameter left
            print('positional parameter left:', leftover)
            return False
        for k, v in zip(self.kwonlyargs, self.kw_defaults):
            if k not in bind and v != None:
                bind[k] = v
        leftover_keys = set(self.kwonlyargs).difference(bind.keys())
        if len(leftover_keys) > 0:
            # keyword-only parameter left
            print('keyword-only parameter left:', leftover_keys)
            return False
        spare_keywords = set(bind.keys()) - self.names
        if self.kwarg == None and len(spare_keywords) > 0:
            # keyword-only parameter left
            print('too many keyword arguments', spare_keywords)
            return False            
        return True

    def __repr__(self):
        pos = ', '.join(self.pos)
        defs = ', '.join('{0}={1}'.format(k,v) for k,v in self.defs)
        varargs = None
        if self.vararg:
            varargs = '*' + self.vararg
            if self.varargannotation:
                varargs += ':' + repr(self.varargannotation)
        kws = ', '.join(('{0}={1}'.format(k, v) if v else k) for k, v in zip(self.kwonlyargs, self.kw_defaults))
        kwargs = '**' + self.kwarg if self.kwarg else None
        
        return '({0})'.format( ', '.join(str(i) for i in [pos, defs, varargs, kws, kwargs, self.bind] if i) )

from typeset import st

# TODO argslist as a class
class TFunc(TObject):
    def __init__(self, args, typefunc, t, bind = None):
        # assert isinstance(typefunc, (_TypeSet, type(None)))
        super().__init__(str(t))
        self.orig_args = args
        self.t = t
        self.args = TArguments(args, bind)
        if t == None:
            self.typefunc = lambda *x : st(TObject(type(None)))
        else:
            self.typefunc = typefunc
    
    def __repr__(self):
        from ast import Call, Name, Load
        c = Call(func=Name(id='x', ctx=Load()), args=[_TypeSet({})], keywords=[], starargs=None, kwargs=None)
        return self.t + ' {0} -> {1}'.format(self.args, self.typefunc(c))

    def with_bind(self, bind):
        return TFunc(self.orig_args, self.typefunc, self.t, bind)
        
    def ismatch(self, actual_args):
        res = self.args.ismatch(actual_args)
        if not res:
            import ast
            print(ast.dump(actual_args))
            print('does not match', repr(self.args))
        return res
        
    def call(self, actual_args):
        if not self.ismatch(actual_args):
            return _TypeSet({})
        return self.typefunc(actual_args)


class _TTuple_Class(_TSeq_Class):
    __metaclass__ = _Singleton

    def __init__(self):
        super().__init__()
        self.generate_methods()
    
    def generate_methods(self):
        import ast
        args = ast.arguments([ast.arg('x', None)], None, None, [], None, None, [], [])
        def getitem(actual_args):
            if not all(hasattr(x, 'value') for x in actual_args.args[0]):
                return self.typeset()
            values = [x.value for x in actual_args.args[0] if isinstance(x.value, int)]
            return _TypeSet(self.types[v] for v in values if v < len(self.types))
        func = TFunc(args, getitem , 'attr')
        self.weak_bind('__getitem__' , _st(func))
    
    def __len__(self):
        return len(self.types)
 
    def can_split_to(self, n):
        return len(self.types) == n
    
    def split_to(self, n):
        assert len(self.types) == n
        return self.types 
 
    def typeset(self):   
        return _TypeSet.union_all(self.types)
       
    def __repr__(self):
        return repr(self.types)

    def new_instance(self, tvalues):
        pass
    
    #def get_dict(self):       return {i:j for i, j in list(self.dict.items()) + list(super.get_dict(self).items())} 


class _TList_Class(_TTuple_Class):
    def __repr__(self):
        return repr(list(self.types))
    
class _TSet_Class(_TTuple_Class):
    def __repr__(self):
        return "Set(" + repr(self.types) + ")"
    
class _TStr_Class(_TTuple_Class):
    def __init__(self, t=str): 
        super().__init__()
    
    def __repr__(self):
        return repr(self.t).split("'")[1]
    
    def typeset(self):   
        return _st(_TStr_Class())

class _TNoneType_Class(TObject_Class):
    def __init__(self): 
        super().__init__()
    
    def __repr__(self):
        return repr('Class NoneType')
    

OBJECT = TObject_Class()
NONE = _TNoneType_Class()

STR = _TStr_Class(str)
BYTES = _TStr_Class(bytes)
INT, FLOAT, COMPLEX = _TInt_Class(), _TFloat_Class(), _TComplex_Class()
TUPLE, LIST, STR, SEQ = _TTuple_Class(), _TList_Class(), _TStr_Class(), _TSeq_Class() 
DICT = _TDict_Class({}, {})
BOOL = _TInt_Class(bool)

from ast import arguments, arg
from helpers import Singleton

class TClass(TObject):
    __metaclass__ = Singleton
    def __init__(self):
        super().__init__('type')
        self.instance_vars = _SymTable()
        params = arguments([arg(name, None) for name in ['self', 'name', 'bases', 'dict'] ], None, None, [], None, None, [], [])
        def __call__(call):
            return self.new_instance(call.args[2], self, call.argc[3])
        call = st(TFunc(params, __call__ , 'attr'))
        self.instance_vars.bind('__call__', call)        
        #self.id = TObject_Class(self.bases, self)
        
    def __repr__(self):
        return "'type'"
    
    def ismatch(self, args):
        x = self.namespace.get_var('__init__', None)
        if x == None:
            return len(args.args)==0
        return x.ismatch(args)
    
    def new_instance(self, cls, body, enclosing = None):
        "create new class object"
        call = body.get_var('__init__')
        class TNew_Class(TObject_Class):
            __metaclass__=_Singleton
            def __init__(self, name):
                super().__init__(name)
        res = TNew_Class('new class')
        if call==None:
            import ast
            args = ast.arguments([ast.arg('self', None)], None, None, [], None, None, [], [])
            def __call__(args):
                return res.new_instance(self.name + ' instance', _TypeSet({}))
            call = st(TFunc(args, __call__ , 'attr'))
        res.weak_bind('__call__', call)
        return res

    def get_type(self):
        return TClass()
    
    def get_symtable(self):
        return self.instance_vars

TYPE = TClass()
    
if __name__=='__main__':
    import analyze
    analyze.main()    