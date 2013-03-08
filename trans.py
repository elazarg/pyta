'''
Created on Mar 6, 2013

@author: elazar
'''

'''
TODO:
* add class instantiation
* add lambda inlining
* find end condition
* limited suppor for list comprehension
* better builtins
* support finite sequences
* fix set/meet bug

--
* constrained attribute assignment
* list tainting
* dictionary support
* set support
* function inlining

--
* general mudolarization and design-level cleanup 
* general code-level cleanup
* basic documentation
'''

import ast
import targettypes as TT
from targettypes import EMPTY, meet
 
messages=[]
def error(*x):
    if x not in messages:
        messages.append(x)

class world:
    _change = True
    @staticmethod
    def changed():
        world._change = True
    
    @staticmethod    
    def is_changed():
        res = world._change
        world._change = False
        return res

def get_classname(node):
    return 'G_' + node.__class__.__name__

def get_class(node):
    clsname = get_classname(node)
    return globals().get(clsname, G_AST)

class G_AST(ast.AST):
    def __init__(self, node, parent):
        self._fields = node._fields
        self.node = node
        self.parent = parent
        
    def add_fields(self, dic):
        self.__dict__.update(dic)
        
    @classmethod
    def create(self, node, parent):
        return self(node, parent)
    
    def get_enclosing(self, tt):
        if isinstance(self.parent, tt):
            return self.parent
        return self.parent.get_enclosing(tt)
    
    def init(self):
        pass
    
class G_slice(G_AST): pass
class G_mod(G_AST): pass
class G_comprehension(G_AST): pass
class G_keyword(G_AST): pass
class G_unaryop(G_AST): pass
class G_operator(G_AST): pass
class G_expr_context(G_AST): pass
class G_cmpop(G_AST): pass
class G_excepthandler(G_AST): pass
class G_withitem(G_AST): pass
class G_boolop(G_AST): pass
class G_alias(G_AST): pass

class G_stmt(G_AST):
    def execute(self):
        pass

class G_expr(G_AST):
    def init(self):
        super().init()
        self.type = EMPTY()

    def get_current_type(self):
        return self.type
    
    def update_type(self):
        raise NotImplementedError()
        
class G_Name(G_expr):
    def __init__(self, *params):
        super().__init__(*params)
        self._refers = None
    
    def get_names(self):
        return {self.id}
    
    def get_refers(self):
        assert self._refers is None or self.id in self._refers.names
        return self._refers
    
    def set_refers(self, nmsp):
        assert self._refers == None
        nmsp.set_single_bind(self)
        self._refers = nmsp
    
    refers = property(get_refers, set_refers)
    
    @classmethod
    def create(self, node, parent):
        node._fields = ('id',)
        if isinstance(node.ctx, ast.Store):
            res = G_SName(node, parent)
        else:
            res = G_LName(node, parent)
        return res
        
class G_SName(G_Name):
    def set_refers(self, nmsp):
        super().set_refers(nmsp)
        self._refers.add_name(self.id)
        
    def update_type(self, newtype):
        # should be called from "Assign", for instance
        self.type = meet(self.type, newtype)
        self._refers.update_sym(self.id, newtype)
        
    refers = property(G_Name.get_refers, set_refers)        
        
class G_LName(G_Name):
    '''
    def update_type(self, newtype):
        #should be called from a definition (or a definition-instance)
        oldtype = self.type
        self.type = meet(self.type, newtype)
        if oldtype != self.type:
            world.changed()
    '''
    def get_current_type(self):
        return self._refers.sym[self.id]
    
class G_arg(G_SName):
    @classmethod
    def create(self, node, parent):
        node._fields = ('id', 'annotation')
        return G_arg(node, parent)
    
    def __init__(self, node, parent):
        self.id = node.arg
        super().__init__(node, parent)
        
class G_Tuple(G_expr):
    def get_names(self):
        return set()
    
    def get_current_type(self):
        return TT.Tuple(n.get_current_type() for n in self.elts)  
 
    def update_type(self, newtype):
        # should be called from "Assign", for instance
        seq = newtype.split_to(len(self.elts))
        for target, value in zip(self.elts, seq):
            target.update_type(value)
    
class G_Assign(G_stmt):
    '''for now, it will be passing around types methodically.
    no actual edge will be placed.'''
    def execute(self):
        for n in self.targets:
            val = self.value.get_current_type()
            n.update_type(val)
            

class G_For(G_stmt):
    def execute(self):
        val = self.iter.get_current_type()
        if isinstance(val, TT.Seq):
            self.target.update_type(val.get_meet_all())

                      
_anything = lambda n : True
def walk(node, to_extend=_anything, to_yield=_anything):
    """
    Recursively yield all descendant nodes in the tree starting at *node*
    (including *node* itself), in no specified order.  This is useful if you
    only want to modify nodes in place and don't care about the context.
    """
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        if to_extend(node):
            todo.extend(ast.iter_child_nodes(node))
        if to_yield(node):
            yield node

def walk_instanceof(node, tt):
    yield from walk(node, to_yield=lambda n : isinstance(n, tt))

def walk_shallow(root, to_yield=_anything):
    extendfunc = lambda n : not isinstance(n, G_def)
    for node in ast.iter_child_nodes(root):
        yield from walk(node, to_yield=to_yield, to_extend=extendfunc)

def walk_shallow_instanceof(node, tt):
    yield from walk_shallow(node, to_yield=lambda n : isinstance(n, tt))
    

class G_def(G_stmt):
    def __init__(self, *params):
        super().__init__(*params)
        
        'all active bindings'
        self.names = set()
        
        'all bindings (id->Name), including lookups'
        self.bindings = {}
        
        from symtable import SymTable
        'all bindings (id->type)'
        self.sym = SymTable()
    
    def set_single_bind(self, name):
        self.bindings.setdefault(name.id, set()).add(name)
            
    def init(self):
        self.target = translate(ast.Name(id=self.name, ctx=ast.Store()))
        self.target.parent = self
        
        self.arg_ids = {i.id for i in walk_shallow_instanceof(self, G_arg)}
        self.local_defs = list(walk_shallow_instanceof(self, G_def))
        nonlocals = walk_shallow_instanceof(self, G_Nonlocal)
        self.nonlocal_ids = set(sum([i.names for i in nonlocals], []))
        self.shallow_names = list(walk_shallow_instanceof(self, G_Name))
        
    def add_name(self, name):
        self.names.add(name)
    
    def print_names(self):
        print(self.name, ':', self.names)
        
    def bind_nonlocals(self, name_to_namespace):
        # add: find kwarg and vararg
        for k in self.arg_ids.intersection(self.nonlocal_ids):
            error('nonlocal {0} is argument'.format(k))
            
        nonlocal_names = [n for n in self.shallow_names
                               if n.id in self.nonlocal_ids]
        for n in nonlocal_names:
            assert n.refers is None
            target = name_to_namespace.get(n.id)
            if target is None:
                error('unbound nonlocal', n.id)
            assert target is not self
            n.refers = target
        # done nonlocal.

    def shallow_bind_locals(self, name_to_namespace):
        from itertools import chain
                
        names = walk_shallow_instanceof(self, G_SName)
        defs = (i.target for i in self.local_defs)
        for n in chain(names, defs):
            if n.refers is None:
                n.refers = self
                name_to_namespace[n.id] = self

    def bind_lookups(self, name_to_namespace):
        lookup = dict.fromkeys(self.module.names, self.module)
        lookup.update(name_to_namespace)
        for n in walk_shallow_instanceof(self, G_LName):
            target = lookup.get(n.id)
            if target is None:
                if n.id in self.module.builtins.names:
                    target = self.module.builtins
                else:
                    error('unbound variable', n.id)
            n.refers = target

    def bind_globals(self, names):
        for n in self.shallow_names:
            if n.id in names:
                n.refers = self.module
        for n in self.arg_ids.intersection(names):
            error('global {0} is argument'.format(n))
        
    def update_sym(self, name, newtype):
        self.sym.bind_type(name, newtype)
        '''
        for n in self.bindings[name]:
            if isinstance(n, G_LName):
                n.update_type(newtype)
        '''
    def get_fully_qualified_name(self):
        return self.get_enclosing(G_def).get_fully_qualified_name() + '.' + self.name
    
    def print_types(self):
        print(self.get_fully_qualified_name(), ':')
        for m in self.names:
            alltypes = [n.get_current_type() for n in self.bindings.get(m, {}) ]
            print(m, TT.meetall(alltypes).tostr())
        print()
        for n in walk_shallow_instanceof(self, (G_ClassDef, G_FunctionDef)):
            n.print_types()           
            
class G_Builtins(G_def):
    def __init__(self, *params):
        self.name = 'builtins'
        super().__init__(*params)
        self.names = {'print'}
        self.bindings = {'print':set()}

class G_Module(G_def, G_mod):
    def __init__(self, *params):
        self.name = '__main__'
        super().__init__(*params)
        self.builtins = G_Builtins(*params)
        
    def init(self):
        super().init()
        for n in walk_instanceof(self, G_def):
            n.module = self
            
            
    def get_fully_qualified_name(self):
        return self.name     
       
    def execute_all(self):
        for _ in range(9):
            for n in walk_instanceof(self, (G_FunctionDef, G_ClassDef)):
                n.execute()
            for n in walk_instanceof(self, (G_Assign, G_For)):
                n.execute()
            # if not world.changed():                break
        self.print_types()
            
    def bind_globals(self):
        self.shallow_bind_locals({})
        # we look first for *all* global bindings, because these can happen anywhere
        # unlike nonlocals, which are more like simple lookups
        for s in walk_instanceof(self, G_Global):
            s.get_enclosing(G_def).bind_globals(s.names)
        self.bind_lookups({})
        # assert: no more globals bindings to handle.
    
    def bind_nonglobals(self):
        for e in self.nonlocal_ids:
            error('global nonlocal declaration:', e)
        for d in self.local_defs:
            d.bind_nonglobals({})
        # self.print_names()
                       
class G_ClassDef(G_def):
    def bind_nonglobals(self, name_to_namespace):
        for d in self.local_defs:
            # here we *do not* pass our local vars
            d.bind_nonglobals(name_to_namespace.copy())
        self.bind_nonlocals(name_to_namespace)
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
        # self.print_names()
    
    def init(self):
        super().init()
        self.type = TT.Class(self.name, self.sym)
    
    def execute(self):
        self.target.update_type(self.type)
                              
class G_Attribute(G_expr):
    def get_current_type(self):
        val = self.value.get_current_type()
        return val.bind_lookups(self.attr)


class G_FunctionDef(G_def):    
    def bind_nonglobals(self, name_to_namespace):
        self.bind_nonlocals(name_to_namespace)
        self.names = self.arg_ids.copy()
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
        for d in self.local_defs:
            d.bind_nonglobals(name_to_namespace.copy())
        # self.print_names()

    def init(self):
        super().init()
        from definitions import Function
        self.type = Function(self)
        #for n in walk_shallow_instanceof(self, G_Return):            print(ast.dump(n))
    
    def execute(self):
        self.target.update_type(self.type)
                        
    def bind_arguments(self, dic):
        for arg in walk_shallow_instanceof(self, G_arg):
            arg.update_type(dic[arg.id])
            
class G_Return(G_Assign):  # instead of inheriting g_stmt
    def __init__(self, *params):
        super().__init__(*params)
        self.targets = [translate(ast.Name(id='return', ctx=ast.Store()))]
        self._fields += ('targets',)

class G_Call(G_expr):
    def get_current_type(self):
        t = self.func.get_current_type()
        #print('calling:',t.tostr())
        return t.call(self)

class G_arguments(G_AST):
    def init(self):   
        if self.vararg:
            self.vararg = translate(ast.arg(self.vararg, self.varargannotation))
            self.vararg.parent = self
        if self.kwarg:
            self.kwarg = translate(ast.arg(self.kwarg, self.kwargannotation))        
            self.kwarg.parent = self
        super().init()
          
        rearg = [i.id for i in self.args]
        size = len(self.defaults)
        self.pos = rearg[:-size] if size > 0 else rearg
        '''
        self.bind = b
        if b is not None:
            del self.pos[0]
        '''
        self.kwonlyargs = [i.id for i in self.kwonlyargs]
        
        self.defs = list(zip(rearg[-size:] , self.defaults))
        self.bind = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  
    '''
    def with_bind(self, t):
        return Arguments(self.arg, t)
    ''' 
    def match(self, actual, bound_arg=None):
        bind = {}
        if bound_arg is not None:
            bind[self.pos[0]]=bound_arg
            pos = self.pos[1:]
        else:
            pos = self.pos[:]
        bind.update(zip(pos, [x.get_current_type() for x in actual.args]))
        i=0
        for keyword in actual.keywords:
            if keyword.arg in bind:
                # double assignment
                error('double assignment: ', keyword.arg)
                return None
            bind[keyword.arg] = keyword.value.get_current_type()
            i+=1
        bind.update([(k, v.get_current_type()) for k, v in self.defs[i:]])                        
        leftover = set(pos) - set(bind.keys())
        if len(leftover) > 0:
            error('positional parameter left:', leftover)
            return None
        for k, v in zip(self.kwonlyargs, self.kw_defaults):
            if k not in bind and v is not None:
                bind[k] = v.get_current_type()
        leftover_keys = set(self.kwonlyargs) - bind.keys()
        if len(leftover_keys) > 0:
            error('keyword-only parameter left:', leftover_keys)
            return None
        spare_keywords = set(bind.keys()) - self.bind
        if self.kwarg == None and len(spare_keywords) > 0:
            error('too many keyword arguments', spare_keywords)
            return None           
        bind[self.vararg.id]=TT.List([v.get_current_type() for v in actual.args[i+1:]])
        #print([(k,v.tostr()) for k,v in bind.items()])
        return bind

    def tostr(self):
        pos = ', '.join(self.pos)
        defs = ', '.join('{0}={1}'.format(k,v.get_current_type().tostr()) for k,v in self.defs)
        varargs = None
        if self.vararg:
            varargs = '*' + self.vararg.id
            if self.vararg.annotation:
                varargs += ':' + repr(self.varargannotation)
        kws = ', '.join(('{0}={1}'.format(k, v.get_current_type().tostr()) if v else k) for k, v in zip(self.kwonlyargs, self.kw_defaults))
        kwargs = '**' + self.kwarg.id if self.kwarg else None
        
        return '({0})'.format( ', '.join(
                             i if isinstance(i, str) else i.tostr()
                             for i in [pos, defs, varargs, kws, kwargs,
                                       #     self.bind
                                       ]
                             if i) )


    
class G_Or(G_boolop): pass
class G_And(G_boolop): pass

class G_ExtSlice(G_slice): pass
class G_Index(G_slice): pass
class G_Slice(G_slice): pass

class G_ExceptHandler(G_excepthandler): pass

class G_AugAssign(G_stmt): pass
class G_ImportFrom(G_stmt): pass
class G_With(G_stmt): pass
class G_Import(G_stmt): pass

class G_Expr(G_stmt): pass
class G_Assert(G_stmt): pass
class G_While(G_stmt): pass
class G_If(G_stmt): pass

class G_Try(G_stmt): pass
class G_Pass(G_stmt): pass
class G_Delete(G_stmt): pass
class G_Continue(G_stmt): pass
class G_Break(G_stmt): pass
class G_Raise(G_stmt): pass

class G_Global(G_stmt): pass
class G_Nonlocal(G_stmt): pass
    
class G_Set(G_expr): pass
class G_Ellipsis(G_expr): pass
class G_Subscript(G_expr): pass
class G_BinOp(G_expr): pass
class G_IfExp(G_expr): pass
# class G_Name(G_expr): pass
# class G_Tuple(G_expr): pass
class G_UnaryOp(G_expr): pass
class G_Dict(G_expr): pass
class G_Starred(G_expr): pass
class G_Lambda(G_expr): pass
class G_GeneratorExp(G_expr): pass
class G_SetComp(G_expr): pass
class G_Compare(G_expr): pass
class G_Bytes(G_expr): pass
class G_BoolOp(G_expr): pass
class G_List(G_expr): pass
class G_ListComp(G_expr): pass
class G_DictComp(G_expr): pass
class G_Yield(G_expr): pass
class G_YieldFrom(G_expr): pass

class G_value(G_expr): pass
    
class G_NameConstant(G_value):
    def init(self):
        c = {None : TT.NONE, False : TT.FALSE, True : TT.TRUE}
        self.type = c[self.value]
        
class G_Str(G_value):
    def init(self):
        self.type = TT.Str(self.s)
        
class G_Num(G_value):
    def init(self):
        types = { int : TT.INT, float : TT.FLOAT, complex : TT.COMPLEX }
        kind = types.get(type(self.n))
        if kind == None:
            print('unknown Num:', ast.dump(self))
            return None
        self.type = TT.Specific.factory(kind, self.n)

        
def translate(node, parent=None):
    """Called if no explicit visitor function exists for a node."""
    C = get_class(node)
    g_parent = C.create(node, parent)
    
    def trans(subnode):
        if isinstance(subnode, ast.AST):
            return translate(subnode, parent=g_parent)
        return subnode
    
    for field, subnode in ast.iter_fields(node):
        if not isinstance(subnode, list):
            value = trans(subnode)
        else:
            value = [trans(item) for item in subnode]
        setattr(g_parent, field, value)
    g_parent.init()
    return g_parent

def build_dataflow(node):
    gast = translate(node)
    gast.bind_globals()
    gast.bind_nonglobals()
    return gast

def test_binding():
    x = ast.parse(open('test/bindings.py').read())
    return build_dataflow(x)
    
def test_dataflow():
    x = ast.parse(open('test.py').read())
    g = build_dataflow(x)    
    g.execute_all()
    for i in messages:
        print(*i)
if __name__ == '__main__':
    # test_binding()
    test_dataflow()


# unknowns or uninteresting:
class G_v(G_mod): pass
class G_Suite(G_mod): pass
# class G_Module(G_mod): pass
class G_Expression(G_mod): pass
class G_Interactive(G_mod): pass

    
# unknowns:
class G_Del(G_expr_context): pass
class G_Load(G_expr_context): pass
class G_Param(G_expr_context): pass
class G_Store(G_expr_context): pass
class G_AugLoad(G_expr_context): pass
class G_AugStore(G_expr_context): pass


# these can probably canonicalized away:

class G_Add(G_operator): pass
class G_Div(G_operator): pass
class G_Sub(G_operator): pass
class G_Pow(G_operator): pass
class G_Mod(G_operator): pass
class G_Mult(G_operator): pass
class G_BitOr(G_operator): pass
class G_LShift(G_operator): pass
class G_BitXor(G_operator): pass
class G_RShift(G_operator): pass
class G_BitAnd(G_operator): pass
class G_FloorDiv(G_operator): pass

class G_Lt(G_cmpop): pass
class G_Is(G_cmpop): pass
class G_Eq(G_cmpop): pass
class G_In(G_cmpop): pass
class G_Gt(G_cmpop): pass
class G_GtE(G_cmpop): pass
class G_LtE(G_cmpop): pass
class G_NotIn(G_cmpop): pass
class G_NotEq(G_cmpop): pass
class G_IsNot(G_cmpop): pass

class G_Not(G_unaryop): pass
class G_USub(G_unaryop): pass
class G_UAdd(G_unaryop): pass
class G_Invert(G_unaryop): pass
