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
                
        names = self.walk_shallow_instanceof(G_Bind_SName)
        defs = (i.target for i in self.walk_shallow_instanceof(G_Bind_def))
        for n in chain(names, defs):
            if n.refers is None:
                n.refers = self
                name_to_namespace[n.id] = self

    def bind_lookups(self, name_to_namespace):
        lookup = dict.fromkeys(self.module.names, self.module)
        lookup.update(name_to_namespace)
        for n in self.walk_shallow_instanceof(G_Bind_LName):
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
    

class G_Bind_def(G_Bind_Namespace):
    def init(self):
        self.local_bind_defs = list(self.walk_shallow_instanceof(G_Bind_def))
        self.arg_ids = {i.id for i in self.walk_shallow_instanceof(G_Bind_arg)}
        nonlocals = self.walk_shallow_instanceof(G_Bind_Nonlocal)
        self.nonlocal_ids = set(sum([i.names for i in nonlocals], []))
        self.shallow_names = list(self.walk_shallow_instanceof(G_Bind_Name))                

class G_Bind_Module(G_Bind_def):
    def init(self):
        super().init()
        for n in self.walk_instanceof(G_Bind_def):
            n.module = self
            
    def bind_globals(self):
        self.find_assign()
        
        self.shallow_bind_locals({})
        # we look first for *all* global bindings, because these can happen anywhere
        # unlike nonlocals, which are more like simple lookups
        for s in self.walk_instanceof(G_Bind_Global):
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
    
class G_Bind_Lambda(G_Bind_Namespace):    
    def bind_nonglobals(self, name_to_namespace):
        self.names = self.arg_ids.copy()
        self.shallow_bind_locals(name_to_namespace)
        self.bind_lookups(name_to_namespace)
        for d in self.local_bind_defs:
            d.bind_nonglobals(name_to_namespace.copy())
            