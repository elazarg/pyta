'''
Created on Mar 6, 2013

@author: elazar
'''

import ast

error = print

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
class G_arg(G_AST): pass
class G_mod(G_AST): pass
class G_comprehension(G_AST): pass
class G_keyword(G_AST): pass
class G_unaryop(G_AST): pass
class G_operator(G_AST): pass
class G_expr_context(G_AST): pass
class G_expr(G_AST): pass
class G_arguments(G_AST): pass
class G_cmpop(G_AST): pass
class G_excepthandler(G_AST): pass
class G_withitem(G_AST): pass
class G_stmt(G_AST): pass
class G_boolop(G_AST): pass
class G_alias(G_AST): pass

class G_Assign(G_stmt):
    def get_binding_place(self):
        for name in self.targets.get_names():
            self.get_create_binder(name).add_binding(name)

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
        self._refers = nmsp
    
    refers = property(get_refers, set_refers)
    
    @classmethod
    def create(self, node, parent):
        node._fields = ['id']
        if isinstance(node.ctx, ast.Store):
            res = G_SName(node, parent)
        else:
            res = G_LName(node, parent)
        return res
        
class G_SName(G_Name):
    def set_refers(self, nmsp):
        super().set_refers(nmsp)
        self._refers.add_name(self.id)
        
    refers = property(G_Name.get_refers, set_refers)        
        
class G_LName(G_Name): pass

class G_Tuple(G_expr):
    def get_names(self):
        return set()

                     
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
        self.names = set()
        self.bindings = set()
        self.global_names = set()
        self.nonlocal_names = set()
        
    def add_name(self, name):
        self.names.add(name)
    
    def print_names(self):
        print(self.name, ':', self.names)
        
    def find_nonlocal_bindings(self, name_to_namespace):
        nonlocal_statements = walk_shallow_instanceof(self, G_Nonlocal)
        for s in nonlocal_statements:
            relevant = lambda k : (
                        isinstance(k, G_Name)
                        and k.id in s.names
                        and k.refers is None)
            for n in walk_shallow(self, relevant):
                target = name_to_namespace.get(n.id)
                if target is not None:
                    n.refers = target
                else:
                    error('unbound nonlocal', n.id)
            for n in walk_shallow_instanceof(self, G_arg):
                if n.arg in s.names:
                    error('nonlocal {0} is argument'.format(n.arg))
        #done nonlocal.

    def lookup(self, name_to_namespace):
        lookup = dict.fromkeys(self.module.names, self.module)
        lookup.update(name_to_namespace)
        for n in walk_shallow_instanceof(self, G_LName):
            target = lookup.get(n.id)
            if target is not None:
                n.refers = target
            else:
                error('unbound variable', n.id)
                
class G_Module(G_def, G_mod):
    def __init__(self, *params):
        self.name='__main__'
        super().__init__(*params)
        
    def find_global_binding(self):
        names = set(walk_shallow_instanceof(self, G_SName))
        for n in names: 
            n.refers = self
        global_statements = walk_instanceof(self, G_Global)
        for s in global_statements:
            nsp = s.get_enclosing(G_def)
            relevant = lambda k : isinstance(k, G_Name) and k.id in s.names
            for n in walk_shallow(nsp, relevant):
                n.refers = self
            for n in walk_shallow_instanceof(nsp, G_arg):
                if n.arg in s.names:
                    error('global {0} is argument'.format(n.arg))
        
        for n in walk_instanceof(self, G_def):
            n.module = self
        #assert: no more globals bindings to handle.
    
    def find_nonglobal_binding(self):
        """searches in inner definitions for both local and nonlocal.
        here we just make sure there aren't any nonlocals"""
        for e in walk_shallow_instanceof(self, G_Nonlocal):
            error('global nonlocal declaration:', e)
        for d in walk_shallow_instanceof(self, G_def):
            #we pass recursively dict<str:G_def> for nonlocal references.
            #it is empty for the global namespace
            d.find_nonglobal_binding({})
        self.print_names()
                       
class G_ClassDef(G_def):
       
    def find_nonglobal_binding(self, name_to_namespace):
        for d in walk_shallow_instanceof(self, G_def):
            #here we *do not* pass our local vars
            d.find_nonglobal_binding(name_to_namespace.copy())
            
        self.find_nonlocal_bindings(name_to_namespace)
        #now find locals
        for n in walk_shallow_instanceof(self, G_SName):
            if n.refers is None:
                n.refers = self
                name_to_namespace[n.id]=self
            
        self.lookup(name_to_namespace)
        self.print_names()
        
            
                   
class G_FunctionDef(G_def):    
    def find_nonglobal_binding(self, name_to_namespace):
        self.find_nonlocal_bindings(name_to_namespace)

        self.names = set(i.arg for i in walk_shallow_instanceof(self, G_arg))        
        #now find locals
        for n in walk_shallow_instanceof(self, G_SName):
            if n.refers is None:
                #otherwise it is global
                n.refers = self
                name_to_namespace[n.id]=self
                
        self.lookup(name_to_namespace)
        
        for d in walk_shallow_instanceof(self, G_def):
            d.find_nonglobal_binding(name_to_namespace.copy())
        self.print_names()
        
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
    gast.find_global_binding()
    gast.find_nonglobal_binding()
    return gast

class G_Or(G_boolop): pass
class G_And(G_boolop): pass

class G_ExtSlice(G_slice): pass
class G_Index(G_slice): pass
class G_Slice(G_slice): pass

class G_AugAssign(G_stmt): pass
class G_Global(G_stmt): pass
class G_Expr(G_stmt): pass
class G_Nonlocal(G_stmt): pass
class G_Try(G_stmt): pass
class G_Pass(G_stmt): pass
class G_ImportFrom(G_stmt): pass
class G_Return(G_stmt): pass
class G_Import(G_stmt): pass
class G_Continue(G_stmt): pass
class G_With(G_stmt): pass
class G_If(G_stmt): pass
#class G_Assign(G_stmt): pass
class G_Assert(G_stmt): pass
class G_Break(G_stmt): pass
class G_Raise(G_stmt): pass
class G_While(G_stmt): pass
class G_Delete(G_stmt): pass
class G_For(G_stmt): pass

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

class G_ExceptHandler(G_excepthandler): pass

class G_v(G_mod): pass
class G_Suite(G_mod): pass
#class G_Module(G_mod): pass
class G_Expression(G_mod): pass
class G_Interactive(G_mod): pass

class G_Del(G_expr_context): pass
class G_Load(G_expr_context): pass
class G_Param(G_expr_context): pass
class G_Store(G_expr_context): pass
class G_AugLoad(G_expr_context): pass
class G_AugStore(G_expr_context): pass

class G_Set(G_expr): pass
class G_Ellipsis(G_expr): pass
class G_Subscript(G_expr): pass
class G_BinOp(G_expr): pass
class G_IfExp(G_expr): pass
#class G_Name(G_expr): pass
#class G_Tuple(G_expr): pass
class G_UnaryOp(G_expr): pass
class G_Yield(G_expr): pass
class G_YieldFrom(G_expr): pass
class G_Dict(G_expr): pass
class G_Call(G_expr): pass
class G_Starred(G_expr): pass
class G_Lambda(G_expr): pass
class G_GeneratorExp(G_expr): pass
class G_SetComp(G_expr): pass
class G_Compare(G_expr): pass
class G_Bytes(G_expr): pass
class G_BoolOp(G_expr): pass
class G_Attribute(G_expr): pass
class G_List(G_expr): pass
class G_ListComp(G_expr): pass
class G_DictComp(G_expr): pass

class G_value(G_expr): pass
    
class G_NameConstant(G_value): pass
class G_Str(G_value): pass
class G_Num(G_value): pass

if __name__=='__main__':
    x=ast.parse(
'''
def foo(x):
    global z
    def bar():
        nonlocal y
        y=2
        b=3
    nonlocal foo
    z=5
    y=4
class A:
    global b
    a=3
    b=2
t=4
'''
    )
    t = build_dataflow(x)
    
    
    

