'''
Created on Feb 28, 2013

@author: elazar
'''
from ast import NodeVisitor 

def tuplesum(iterable):
    return sum( iterable, () )

class LocalBindingFinder(NodeVisitor):
    '''
    The following constructs bind names:
     formal parameters to functions,
     import statements, 
     class and function definitions, 
     targets that are identifiers if occurring in an
         assignment
         for loop header
         after as in a with statement or except clause. 
     A target occurring in a del statement is also considered bound for this purpose.
    
    Each assignment or import statement occurs within a block defined by a class or function definition or at the module level (the top-level code block).
    
    '''
    def generic_visit(self, node):
        return ()
    
    def visit_Name(self, node):
        return node.id

    def visit_Tuple(self, node):
        return tuple(self.visit(x) for x in node.elts)

    visit_List = visit_Tuple

    def visit_Starred(self, node):
        return (self.visit(node.value),)
    
    def visit_alias(self, node):
        if node.asname:
            return (node.asname, ) 
        if node.name=='*':
            #should import everything, but it's too hard
            return ()
        return (node.name, )
    
    def visit_Import(self, node):
        return tuplesum(self.visit(name) for name in node.names)

    visit_ImportFrom = visit_Import
    visit_Del = visit_Import
    
    def visit_Assign(self, node):
        return tuple(self.visit(x) for x in node.targets)
    
    def visit_FunctionDef(self, node):
        return (node.name, )

    visit_AugAssign = visit_ClassDef = visit_FunctionDef
    
    def visit_For(self, node):
        header = self.visit(node.target)
        return header + find_bindings(node)
    
    def visit_With(self, node):
        header = tuple(item.optional_vars.id
                       for item in node.items
                       if item.optional_vars is not None)
        return header + find_bindings(node)
    
    def visit_ExceptHandler(self, node):
        return (node.name,) + find_bindings(node)
        
    def bodyvisit(self, node):
        return find_bindings(node)
    
    visit_Try = visit_While = visit_If = bodyvisit

class Names:
    def __init__(self, localvars, nonlocalvars, globalvars):
        self.locals = localvars
        self.nonlocals = nonlocalvars
        self.globals = globalvars

class UnLocalBindingFinder(NodeVisitor):
    def __init__(self):
        self.globals = {}
        self.nonlocals = {}
        
    def visit_FunctionDef(self, node):
        pass
    
    visit_ClassDef = visit_FunctionDef
    
    def visit_Nonlocal(self, node):
        self.nonlocals.update(node.names)
        
    def visit_Global(self, node):
        self.globals.update(node.names)

def find_bindings(node):
    from ast import iter_fields 
    res = ()
    bf = LocalBindingFinder()
    for name, body in iter_fields(node):
        if name in ('body', 'orelse', 'handlers', 'finalbody'):
            res += tuplesum(bf.visit(stmt) for stmt in body)
    un = UnLocalBindingFinder()
    un.visit(node)
    return Names(set(res), un.nonlocals, un.globals)


if __name__=='__main__':
    from ast import parse
    fp = parse(open('visitor.py').read())
    print(find_bindings(fp))
    