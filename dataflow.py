'''
Created on Mar 1, 2013

@author: elazar
'''
import networkx as nx
import ast


class Visitor(ast.NodeVisitor):
    count=0
    def add_node(self, node):
        self.count += 1
        node.id = self.count
        self.g.add_node(node)

    def add_edge(self, edge):
        for k in edge:
            self.add_node(k)
        self.g.add_edge(edge)
    
    def generic_visit(self, node):
        self.add_node(node)
        super().generic_visit(self, node)
    
    def __init__(self, parent):
        g=nx.DiGraph()

    def visit_Module(self, node):
        return self.generic_visit(node)
   
    def visit_Assign(self, node):
        value = self.visit(node.value)
        for target in node.targets:
            self.add_edge(target, value)
            
    '''            
        def visit_Attribute(self, attr):
            pass
    
        def visit_FunctionDef(self, func):
            pass
        
        def visit_ClassDef(self, cls):
            pass
                
        def visit_Call(self, value):
            pass
                
        def visit_IfExp(self, ifexp):
            pass
        
        def visit_Subscript(self, sub):
            pass
    
        def visit_BinOp(self, binop):
            pass
        
        def visit_If(self, stat):
            pass
        
        def visit_While(self, stat):
            pass
        
        def visit_For(self, stat):
            pass
        
        def visit_Return(self, ret):
            pass
    
    '''
            
    def visit_Str(self, node):
        self.add_node(node)
        return node
    
    visit_NameConstant = visit_Num = visit_Bytes = visit_Str
    '''
    def visit_Dict(self, value):
        pass
    
    def visit_Tuple(self, value):
        pass
        
    def visit_List(self, value):
        pass

    '''
    
    def visit_Name(self, value):
        nodes = self.find_bindings(value.id)
        for k in nodes:
            self.add_edge( (k, value) )
        
    '''
        return c[cons.value]

    def visit_ListComp(self, value):
        pass
 
    def visit_Lambda(self, lmb):
        pass
    
    def visit_Expr(self, expr):
        pass
    
    def visit_arguments(self, args):
        pass
        