'''
Created on Mar 11, 2013

@author: elazar
'''

'''
This module is about finding the binding of a variable.
There are five possibilities:
1 local
2 global
3 nonlocal 
4 formal parameter
5 builtins
'''

import ast
error = print                  
_anything = lambda n : True


class G_Bind_Global: pass
class G_Bind_Nonlocal: pass


class G_Bind_expr:
    pass

class G_Bind_Name:
    def __init__(self, *params):
        self._refers = None
    
    def get_names(self):
        return {self.id}
    
    def get_refers(self):
        assert self._refers is None or self.id in self._refers.names
        return self._refers
    
    def set_refers(self, nmsp):
        assert self.refers is None
        nmsp.set_single_bind(self)
        self._refers = nmsp
    
    refers = property(get_refers, set_refers)
        
class G_Bind_SName(G_Bind_Name):
    def set_refers(self, nmsp):
        super().set_refers(nmsp)
        self._refers.add_name(self.id)
        
    refers = property(G_Bind_Name.get_refers, set_refers)        
        
class G_Bind_LName(G_Bind_Name):
    pass

class G_Bind_DelName(G_Bind_Name):
    pass

class G_Bind_arg(G_Bind_SName):
    pass
 
class G_Bind_Assign:
    pass

class G_Bind_withitem:
    pass
            
class G_Bind_For:
    pass

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
    extendfunc = lambda n : not isinstance(n, G_Bind_def)
    for node in ast.iter_child_nodes(root):
        yield from walk(node, to_yield=to_yield, to_extend=extendfunc)

def walk_shallow_instanceof(node, tt):
    yield from walk_shallow(node, to_yield=lambda n : isinstance(n, tt))
    
class G_Bind_Namespace:
    def __init__(self, *params):        
        'all active bindings'
        self.names = set()
        'all bindings (id->Name), including lookups'
        self.bindings = {}

        self.local_bind_defs = []

    def set_single_bind(self, name):
        self.bindings.setdefault(name.id, set()).add(name)
    
    def add_name(self, name):
        self.names.add(name)
    
    def print_names(self):
        print(self.name, ':', self.names)

    def bind_nonlocals(self, name_to_namespace):
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
                
        names = walk_shallow_instanceof(self, G_Bind_SName)
        defs = (i.target for i in self.local_bind_defs)
        for n in chain(names, defs):
            if n.refers is None:
                n.refers = self
                name_to_namespace[n.id] = self

    def bind_lookups(self, name_to_namespace):
        lookup = dict.fromkeys(self.module.names, self.module)
        lookup.update(name_to_namespace)
        for n in walk_shallow_instanceof(self, G_Bind_LName):
            target = lookup.get(n.id)
            if target is None and n.id in self.module.builtins.names:
                target = self.module.builtins
            if target is None: 
                error('unbound variable', n.id)
            else:
                n.refers = target

    def bind_globals(self, names):
        for n in self.shallow_names:
            if n.id in names:
                n.refers = self.module
        for n in self.arg_ids.intersection(names):
            error('global {0} is argument'.format(n))
        
    def get_fully_qualified_name(self):
        return self.get_enclosing(G_Bind_def).get_fully_qualified_name() + '.' + self.name

class G_Bind_def(G_Bind_Namespace):
    def init(self):
        self.local_bind_defs = list(walk_shallow_instanceof(self, G_Bind_def))                

class G_Bind_Module(G_Bind_def):
    def init(self):
        super().init()
        for n in walk_instanceof(self, G_Bind_def):
            n.module = self
            
    def get_fully_qualified_name(self):
        return self.name     
    
    def find_assign(self):
        self.defs = list(walk_instanceof(self, (G_Bind_FunctionDef, G_Bind_ClassDef)))
        if self.builtins:
            self.defs += list(walk_instanceof(self.builtins, (G_Bind_FunctionDef, G_Bind_ClassDef))) 
        self.assigns = list(walk_instanceof(self, (G_Bind_Assign, G_Bind_For, G_Bind_withitem)))
        
    def bind_globals(self):
        self.find_assign()
        
        self.shallow_bind_locals({})
        # we look first for *all* global bindings, because these can happen anywhere
        # unlike nonlocals, which are more like simple lookups
        for s in walk_instanceof(self, G_Bind_Global):
            s.get_enclosing(G_Bind_def).bind_globals(s.names)
        self.bind_lookups({})
        # assert: no more globals bindings to handle.
    
    def bind_nonglobals(self):
        for e in self.nonlocal_ids:
            error('global nonlocal declaration:', e)
        for d in self.local_bind_defs:
            d.bind_nonglobals({})
        # self.print_names()
                       
class G_Bind_ClassDef(G_Bind_def):
    def bind_nonglobals(self, name_to_namespace):
        for d in self.local_bind_defs:
            # here we *do not* pass our local vars
            d.bind_nonglobals(name_to_namespace.copy())
        self.bind_nonlocals(name_to_namespace)
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
    
class G_Bind_FunctionDef(G_Bind_def):    
    def bind_nonglobals(self, name_to_namespace):
        self.bind_nonlocals(name_to_namespace)
        self.names = self.arg_ids.copy()
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
        for d in self.local_bind_defs:
            d.bind_nonglobals(name_to_namespace.copy())
        
class G_Bind_Comprehension(G_Bind_Namespace):    
    def bind_nonglobals(self, name_to_namespace):
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
        