'''
Created on Feb 28, 2013

@author: elazar
'''
from ast import NodeVisitor, dump

def tuplesum(iterable):
    return sum( iterable, () )


class LocalBindingFinder(NodeVisitor):
    def __init__(self):
        self.globals = set()
        self.nonlocals = set()
        
    def generic_visit(self, node):
        'assuming node is stmt'
        #print(node)
        return [ ]
    
    #actual bindings:    
    def visit_Import(self, node):
        return [(self.visit(name)[0], node) for name in node.names]
    
    visit_ImportFrom = visit_Import
    visit_Del = visit_Import

    def visit_AugAssign(self, node):
        return [(self.visit(node.target)[0], node)]
    
    def visit_Assign(self, node):
        return [(name, node) for name in sum([self.visit(x) for x in node.targets], [])]
    
    def visit_FunctionDef(self, node):
        return [ (node.name, node) ]

    visit_ClassDef = visit_FunctionDef
    
    def visit_For(self, node):
        header = [(name, node) for name in self.visit(node.target)]
        return header + self.find_simple_bindings(node)
    
    def visit_With(self, node):
        header = [ (item.optional_vars.id, item)
                       for item in node.items
                       if item.optional_vars is not None]
        return header + self.find_simple_bindings(node)
    
    def visit_ExceptHandler(self, node):
        return [ (node.name, node) ] + self.find_simple_bindings(node)
      
    def bodyvisit(self, node):
        return self.find_simple_bindings(node)
    
    visit_Try = visit_While = visit_If = bodyvisit
    
    #helpers
    def visit_Name(self, node):
        return [node.id]
    
    def visit_Attribute(self, node):
        'return tuple, not simple name'
        return [str(self.visit(node.value)[0]) + '.' + node.attr]

    def visit_Tuple(self, node):
        return sum([self.visit(x) for x in node.elts], [])

    visit_List = visit_Tuple

    def visit_Call(self, node):
        #ignore complicated possibilities
        return [self.visit(node.func)[0] + '()']
    
    def visit_Subscript(self, node):
        #ignore complicated possibilities
        return [self.visit(node.value)[0] + '[]']

    def visit_Starred(self, node):
        return self.visit(node.value)
    
    def visit_alias(self, node):
        if node.asname:
            return [node.asname]
        '''
        if node.name=='*':
            #should import everything, but it's too hard
            return ()
        '''
        return [node.name]

    def visit_Nonlocal(self, node):
        self.nonlocals.update(node.names)
        return []
        
    def visit_Global(self, node):
        self.globals.update(node.names)
        return []
        
    def visit_arg(self, node):
        return (node.arg, node)
    
    def visit_arguments(self, node):
        
        import ast
        args = [self.visit(p) for p in node.args]
        if node.vararg is not None:
            args += [(node.vararg, ast.arg(node.vararg, []))]
        for i, (p, n) in enumerate(args):
            n.pos = i 
        namedargs = [p.arg for p in node.kwonlyargs]
        if node.kwarg is not None:
            namedargs += [(node.kwarg, ast.arg(node.kwarg, {}))]
        for p,n  in namedargs:
            p.pos = None
        return args + namedargs
    
    def find_simple_bindings(self, node) -> list:
        'returns a list<name, node> with all local occurences of binding statements'
        from ast import iter_fields 
        res = []
        for name, body in iter_fields(node):
            if name in ('body', 'orelse', 'handlers', 'finalbody'):
                res += sum( (self.visit(stmt) for stmt in body) , [])
            if name == 'args':
                args = self.visit(body)
                for (_, n) in args:
                    n.lineno = node.lineno
                res += args
                
        return res
    
class Names:
    def __init__(self, localvars, nonlocalvars, globalvars):
        self.locals = localvars
        self.nonlocals = nonlocalvars
        self.globals = globalvars
               
def find_bindings(node) -> Names:
    local_names = []
    global_names = []
    nonlocal_names = []
    bf =  LocalBindingFinder()
    for name, v in bf.find_simple_bindings(node):
        if name in bf.globals:
            target = global_names
        elif name in bf.nonlocals:
            target = nonlocal_names
        else:
            target = local_names
        target.append( (name, v) )
    #we lose information about global/nonlocal declaration *without* bindings.
    #it seems OK though.
     
    return Names(local_names, nonlocal_names, global_names)

def get_depth_lookups(root, depth=-1):
    import ast
    for node in ast.iter_child_nodes(root):
        if isinstance(node, ast.Name): # and isinstance(node.ctx, ast.Load):
            yield node
        elif not isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            yield from get_depth_lookups(node, depth)
        elif depth != 0:
            yield from get_depth_lookups(node, depth-1)

def fst(seq):
    return [t[0] for t in seq]

class Namespace:
    globalname = '' #can be '__main__ 
    '''
    A node in the syntax tree. have a dictionary<name, set of binding places>
    '''
    def __init__(self, node, parent):
        import ast
        self.node = node
        self.name = parent.name + node.name + ('.' if isinstance(node, ast.ClassDef) else ':')
        self.parent = parent
        self.globals = self.parent.globals
        self.depth = self.parent.depth + 1
    
    def __eq__(self, other):
        return self.node == other.node
    
    def __hash__(self):
        return hash(self.node)
    
    def make_namespaces(self):
        self.bindings = bindings = find_bindings(self.node)
        self.locals = set(bindings.locals)
        #patchwork
        for n in self.locals:
            n[1].namespace = self.name
        self.bind_globals(bindings.globals)
        self.bind_nonlocals(bindings.nonlocals)
        self.create_children()
        self.update_lookups()
        
    def bind_globals(self, global_vars):
        'globals are updated even there there was not such name'
        self.global_bindings = set(global_vars)
        #self.global_bindings.update(self.globals)
           
    def bind_nonlocals(self, nonlocal_vars):
        'nonlocals are searched for.'
        for name, node in nonlocal_vars:
            self.parent.nonlocal_update(name, node)                

    def nonlocal_update(self, name, item):
        if name in (item[0] for item in self.locals):
            self.locals.add( (name, item) )
        else:
            self.parent.nonlocal_update(name, item)
    
    def create_children(self):
        from ast import ClassDef, FunctionDef
        self.definitions = set()
        self.vars = set()
        def mylen():
            return sum(len(i) for i in
                  [self.definitions, self.locals,
                   self.vars, self.globals ]) 
        while True:
            '''we loop here because new definitions in local environment
            can be done in nested defintions'''
            size = mylen() 
            for name, node in self.locals:
                if isinstance(node, (ClassDef, FunctionDef)):
                    self.definitions.add(Namespace(node, self))
                else:
                    self.vars.add( name )
            for d in self.definitions:
                d.make_namespaces()
            if size == mylen():
                break

    def lookup(self, name:str):
        if name in fst(self.locals):
            return self.name
        return self.parent.lookup(name)
        
    def update_lookups(self):
        for name in get_depth_lookups(self.node, 0):
            #print(fst(self.global_bindings))
            if name in fst(self.global_bindings):
                name.namespace = Namespace.globalname
            else:
                name.namespace = self.lookup(name.id)
        for d in self.definitions:
            d.update_lookups()
        
    def tostr(self):
        res = ' ' * self.depth + str(self.node.name) + ' ' +  str(self.node.lineno)
        if len(self.locals) > 0:
            res += ':\n'
            for name in self.vars:
                res += ' ' * (self.depth+1) + str(name) + ' '
                res += ', '.join(str(t[1].lineno) for t in self.locals if t[0]==name)
                res += '\n'
            
        res += '\n'.join(x.tostr() for x in self.definitions)
        return res

class GlobalNamespace(Namespace):
    '''
    A node in the syntax tree. have a dictionary<name, set of binding places>
    '''
    def __init__(self, node):
        node.name = '__main__'
        self.name=Namespace.globalname
        node.lineno = 0
        self.node = node
        self.depth = 0
   
    def bind_globals(self, global_vars):
        'globals are updated even there there was not such name'
        self.globals = self.locals
        super().bind_globals(global_vars)
                           
    def bind_nonlocals(self, nonlocals):
        for name, node in nonlocals:
            self.nonlocal_update(name, node)       

    def nonlocal_update(self, name, node):
        print('nonlocal error: {0}'.format(name))
 
    def lookup(self, name:str):
        if name in fst(self.locals):
            return self.name
        return None

if __name__=='__main__':
    from ast import parse
    fp = parse(open('test.py').read())
    b = GlobalNamespace(fp)
    b.make_namespaces()
    print(b.tostr())
    for i in get_depth_lookups(fp):
        print(i.id, i.namespace)
    