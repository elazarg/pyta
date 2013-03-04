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
--
* Namespace - collection of 'name' nodes
'''

class GraphNode:
    pass

class GBinding(GraphNode):
    '''These nodes serve as kind of multiplexer - 
    controlling flow of type information from expressions to names.'''
    pass
 
class GNameDef(GBinding):
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return '*'+str(self.name)
       
class GAssign(GBinding):
    'only for the tuple case'
    def __init__(self, targets, value):
        self.targets = tuple(GNameDef(i.id) for i in targets)
        self.value = value
    
    def __repr__(self):
        left = tuple(self.targets) if len(self.targets) > 1 else self.targets[0]
        return str(left) + '=' + str(self.value)

class GFor(GBinding):
    def __init__(self, target, iterable):
        self.target = target
        self.iter = iterable
    
    def __repr__(self):
        return 'for ' + str(self.target) + ' in ' + str(self.iter)

class GExpression(GraphNode):
    def __init__(self, mytype):
        self.mytype = mytype

class GName(GExpression):
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return str(self.name)

class GCall(GExpression):
    #TODO : add function-call type
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return str(self.name)

class GTuple(GExpression):
    def __init__(self, tuplist):
        self.tuplist = tuple(tuplist)

    def __eq__(self, other):
        return isinstance(other, GTuple) and self.tuplist == other.tuplist

    def __hash__(self):
        return hash(self.tuplist)
             
    def __repr__(self):
        return str(tuple(self.tuplist))

class GList(GTuple):
    def __repr__(self):
        return str(self.tuplist)

class GValue(GExpression):
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, GValue) and self.value == other.value

    def __hash__(self):
        return hash(self.value)
            
    def __repr__(self):
        return '<{0}>'.format(self.value)
    
class GNum(GValue):    pass
class GStr(GValue):    pass
class GConstant(GValue):    pass
        
from bindfind import GlobalNamespace 
class GraphCreator(ast.NodeVisitor):
    def __init__(self):
        self.g = nx.DiGraph()
        
    def build(self, node):
        self.ns = GlobalNamespace(node)
        self.ns.make_namespaces()
        for name, node in self.ns.locals:
            self.g.add_edge(self.visit(node), GNameDef(name))      
    
    def printme(self):
        for i in self.g.edges():
            print(str(i))
        #self.visit(node)

    def visit_Name(self, node):
        'this is for NameExpressions ONLY'
        if isinstance(node.ctx, ast.Load):
            return GName(node.id)
        return GNameDef(node.id)
    
    def visit_Assign(self, node):
        value = self.visit(node.value)
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return value
        if isinstance(target, ast.Tuple):
            #targets = [self.visit(i) for i in node.targets]
            res = GAssign(target.elts, value)
            #self.g.add_edge(value, res)
            return res
        assert False
        
    def visit_For(self, node):
        iterable = self.visit(node.iter)
        res = GFor(self.visit(node.target), iterable)
        self.g.add_edge(iterable, res)
        return res
    
    def visit_Num(self, node):
        return GNum(node.n)
    
    def visit_NameConstant(self, node):
        return GConstant(node.value)
    
    def makeseq(self, node, T):
        'looks like duplicate bookkeeping for these nodes'
        tup = [self.visit(i) for i in node.elts]
        res = T(tup)
        for v in tup:
            self.g.add_edge(v, res)
        return res
    
    def visit_Tuple(self, node):
        return self.makeseq(node, GTuple)

    def visit_List(self, node):
        return self.makeseq(node, GList)
    
if __name__=='__main__':
    from ast import parse
    fp = parse(open('test.py').read())
    b = GraphCreator()
    b.build(fp)
    b.printme()
        
    
    