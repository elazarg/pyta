'''
Created on Mar 1, 2013

@author: elazar
'''
import networkx as nx
import ast

'''
Edges represent passage of type information.

Types of vertices in the dataflow graph:
* Name - simple string
* Namespace - collection of 'name' nodes
* Binding - node that feeds one or more Name nodes
  * Assign
  * AugAssign
  * For
  * With
  * Except
  * Definitions:
      * Function
      * Class  
* Expression - node that have a Type and feeds it to another node
  * Value - expression with known type
      * Num
      * NameConstant
      * Str
  * Call - linked to name and arguments
  * Lambda
  * NameExpression - linked to Namespace
  * Attribute ? - grows edges 'dynamically'
'''

class GraphNode:
    pass

class GBinding(GraphNode):
    pass

class GAssign(GBinding):
    def __init__(self, targets, value):
        self.targets = targets
        self.value = value
    
    def __repr__(self):
        return str(self.targets) + '=' + str(self.value)

class GFor(GBinding):
    def __init__(self, target, iterable):
        self.target = target
        self.iter = iterable
    
    def __repr__(self):
        return 'for ' + str(self.target) + ' in ' + str(self.iter)
  
class GNum(GraphNode):
    def __init__(self, value):
        self.value = value
        
    def __repr__(self):
        return str(self.value)

class GName(GraphNode):
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return str(self.name)

from bindfind import GlobalNamespace 
class GraphCreator(ast.NodeVisitor):
    def __init__(self):
        self.g = nx.DiGraph()
        
    def build(self, node):
        self.ns = GlobalNamespace(node)
        self.ns.make_namespaces()
        for name, node in self.ns.locals:
            self.g.add_edge(self.visit(node), GName(name))      
        print(str(self.g.edges()))
        #self.visit(node)

    def visit_Name(self, node):
        return GName(node.id)
    
    def visit_Assign(self, node):
        targets = [self.visit(i) for i in node.targets]
        value = self.visit(node.value)
        res = GAssign(targets, value)
        self.g.add_edge(value, res)
        return res
    
    def visit_For(self, node):
        iterable = self.visit(node.iter)
        res = GFor(self.visit(node.target), iterable)
        self.g.add_edge(iterable, res)
        return res
    
    def visit_Num(self, node):
        return GNum(node.n)
    
    def visit_Tuple(self, node):
        return [self.visit(i) for i in node.elts]
    
if __name__=='__main__':
    from ast import parse
    fp = parse(open('test.py').read())
    b = GraphCreator()
    b.build(fp)
    
        
    
    