'''
Created on Mar 6, 2013

@author: elazar
'''

'''
TODO:
* find end condition
* limited support for list comprehension
* support finite sequences

--
* add lambda inlining
* constrained attribute assignment
* list tainting
* dictionary support
* better builtins
* set support
* function inlining

--
* general modularization and design-level cleanup 
* general code-level cleanup
* basic documentation
'''

#import ast
import targettypes as TT
from targettypes import EMPTY, meet, meetall
from binder import *

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

def get_class(node):
    return globals().get('G_' + node.__class__.__name__, node.__class__)

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
class G_cmpop(G_AST): pass
class G_excepthandler(G_AST): pass
class G_alias(G_AST): pass

# unknowns or uninteresting:
class G_v(G_mod): pass
class G_Suite(G_mod): pass
# class G_Module(G_mod): pass
class G_Expression(G_mod): pass
class G_Interactive(G_mod): pass

    
class G_expr_context(G_AST): pass
class G_Store(G_expr_context): pass
class G_Load(G_expr_context): pass
class G_Del(G_expr_context): pass
# unknowns:
class G_Param(G_expr_context): pass
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
        G_expr.__init__(self, *params)
        G_Bind_Name.__init__(self)
    
    @classmethod
    def create(self, node, parent):
        node._fields = ('id',)
        if isinstance(node.ctx, ast.Store):
            res = G_SName(node, parent)
        else:
            res = G_LName(node, parent)
        return res
        
class G_SName(G_Name, G_Bind_SName):
    def __init__(self, *params):
        G_Name.__init__(self, *params)
        G_Bind_SName.__init__(self)
                    
    def update_type(self, newtype):
        # should be called from "Assign", for instance
        self.type = meet(self.type, newtype)
        self.refers.update_sym(self.id, newtype)        
        
class G_LName(G_Name, G_Bind_LName):        
    def __init__(self, *params):
        G_Name.__init__(self, *params)
        G_Bind_LName.__init__(self)

    def get_current_type(self):
        return self.refers.sym[self.id]
    
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
            
class G_With(G_stmt): pass

class G_withitem(G_AST):
    def execute(self):
        if self.optional_vars is not None:
            val = self.context_expr.get_current_type()
            t = val.filter(lambda x :
                            x.bind_lookups('__enter__')
                             and x.bind_lookups('__exit__'))
            self.optional_vars.update_type(t)
            
class G_For(G_stmt):
    def execute(self):
        val = self.iter.get_current_type()
        t = val.filter(lambda x : isinstance(x, TT.Seq))
        self.target.update_type(t.get_meet_all())

class G_def(G_stmt, G_Bind_def):
    def __init__(self, *params):
        G_stmt.__init__(self, *params)
        G_Bind_def.__init__(*params)
        from symtable import SymTable
        'all bindings (id->type)'
        self.sym = SymTable()
        self.isbuiltin = False
        
    def make_selfname(self):
        self.target = translate(ast.Name(id=self.name, ctx=ast.Store()))
        self.target.parent = self
        
    def init(self):
        self.make_selfname()
        self.arg_ids = {i.id for i in walk_shallow_instanceof(self, G_arg)}
        self.local_defs = list(walk_shallow_instanceof(self, G_def))
        nonlocals = walk_shallow_instanceof(self, G_Nonlocal)
        self.nonlocal_ids = set(sum([i.names for i in nonlocals], []))
        self.shallow_names = list(walk_shallow_instanceof(self, G_Name))
        
    def add_name(self, name):
        self.names.add(name)
    
    def print_names(self):
        print(self.name, ':', self.names)

    def update_sym(self, name, newtype):
        self.sym.bind_type(name, newtype)
        
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
    busy = False
    
    @staticmethod
    def create(*params):
        if G_Builtins.busy:
            return None
        G_Builtins.busy = True
        g = build_files(['database/functions.py',
                        'database/int.py',
                        'database/str.py',
                        'database/float.py',
                        'database/complex.py',
                        'database/object.py',
                        'database/list.py'
                        ])
        return g

class G_Module(G_def, G_mod, G_Bind_Module):
    def __init__(self, *params):
        self.name = '__main__'
        super().__init__(*params)
        G_Bind_Module.__init__(self)
        self.builtins = G_Builtins.create(*params)
        
    def init(self):
        super().init()
        for n in walk_instanceof(self, G_def):
            n.module = self
            
    def get_fully_qualified_name(self):
        return self.name     
       
    def execute_all(self):
        self.isbuiltin = G_Builtins.busy        
        for _ in range(9):
            if self.builtins:
                self.builtins.execute_all()
            for n in self.defs:
                n.execute()
            for n in self.assigns:
                n.execute()
            # if not world.changed():                break
    
    def find_assign(self):
        self.defs = list(walk_instanceof(self, (G_FunctionDef, G_ClassDef)))
        if self.builtins:
            self.defs += list(walk_instanceof(self.builtins, (G_FunctionDef, G_ClassDef))) 
        self.assigns = list(walk_instanceof(self, (G_Assign, G_For, G_withitem)))
                       
class G_ClassDef(G_def, G_Bind_ClassDef):
    def __init__(self, *params):
        super().__init__(*params)
        G_Bind_ClassDef.__init__(self)
    
    def init(self):
        G_def.init(self)
        if G_Builtins.busy and self.name in TT.name_to_type: 
            self.type = TT.name_to_type[self.name]
            self.type.sym = self.sym
        else:
            self.type = TT.Class(self.name, self.sym)
    
    def execute(self):
        self.target.update_type(self.type)

class G_FunctionDef(G_def, G_Bind_FunctionDef):
    def __init__(self, *params):
        G_def.__init__(self, *params)
        G_Bind_FunctionDef.__init__(self)
        
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
            
    def get_return(self):
        res = self.sym['return']
        if self.isbuiltin:
            res = res.get_unspecific()
        return res
    
class G_Lambda(G_FunctionDef, G_expr):
    def __init__(self, *params):
        self.name = 'lambda'
        super().__init__(*params)
            
    def make_selfname(self):
        pass
    
    def execute(self):
        pass
        
    def get_return(self):
        return self.body.get_current_type()
                              
class G_Attribute(G_expr):
    def get_current_type(self):
        val = self.value.get_current_type()
        return val.bind_lookups(self.attr)

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

def meet_from(iterable):
    return meetall(i.get_current_type() for i in iterable)

class G_IfExp(G_expr):
    def get_current_type(self):
        return meet_from([self.body, self.orelse])
    
class G_BoolOp(G_expr):
    def get_current_type(self):
        return meet_from(self.values)
     
class G_Or(G_BoolOp): pass
class G_And(G_BoolOp): pass

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
        self.kwonlyargs = [i.id for i in self.kwonlyargs]
        
        self.defs = list(zip(rearg[-size:] , self.defaults))
        self.bind = set(rearg + [self.vararg] + self.kwonlyargs + [self.kwarg])  

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
        if self.vararg:
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




class G_ExtSlice(G_slice): pass
class G_Index(G_slice): pass
class G_Slice(G_slice): pass

class G_ExceptHandler(G_excepthandler): pass

class G_AugAssign(G_stmt): pass
class G_ImportFrom(G_stmt): pass
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

class G_Global(G_stmt, G_Bind_Global): pass
class G_Nonlocal(G_stmt, G_Bind_Global): pass
    
class G_Set(G_expr): pass
class G_Ellipsis(G_expr): pass
class G_Subscript(G_expr): pass
class G_BinOp(G_expr): pass
class G_UnaryOp(G_expr): pass
class G_Dict(G_expr): pass
class G_Starred(G_expr): pass
class G_GeneratorExp(G_expr): pass
class G_SetComp(G_expr): pass
class G_Compare(G_expr): pass
class G_Bytes(G_expr): pass
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
    g_parent = get_class(node).create(node, parent)
    
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
    
def build_files(filelist=['test.py']):
    x = ast.parse(open(filelist[0]).read())
    for file in filelist[1:]:
        x.body.extend(ast.parse(open(file).read()).body)
    from ast_transform import trans
    t = trans(x)
    g = build_dataflow(t)    
    g.execute_all()
    return g

if __name__ == '__main__':
    # test_binding()
    g = build_files()
    g.print_types()
    for i in messages:
        print(*i)


