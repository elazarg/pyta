'''
Created on Mar 1, 2013

@author: elazar
'''
import networkx as nx
import ast
from codegen import to_source
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
import targettypes as TT

class GraphNode:
    def assign_node(self, node):
        self.id = id(node)
        
    def get_id(self):
        return self.id
    
    def __hash__(self):
        return hash(self.get_id())
    
    def __eq__(self, other):
        assert isinstance(other, GraphNode)
        return self.get_id() == other.get_id()

class GBinding(GraphNode):
    '''These nodes serve as kind of multiplexer - 
    controlling flow of type information from expressions to names.'''
    pass
 
class GNameSpace(GBinding):
    pass

class GClassDef(GNameSpace):
    def __init__(self, name, namespace):
        self.name = name
        self.namespace = namespace
        
    def __repr__(self):
        return 'class ' + self.name + repr(self.namespace)

class GFunctionDef(GNameSpace):
    def __init__(self, node, mytype):
        self.name = node.name
        self.type = mytype
        
    def __repr__(self):
        return 'def ' + self.name

class GArguments(GBinding):
    def __init__(self, args):
        from definitions import Arguments
        'constraints: value is splitable to len(targets) recursively'
        self.target = Arguments(args)
        self.id = self.target
    
    def __repr__(self):
        return self.target.tostr()
  
class GTupleAssign(GBinding):
    'only for the tuple case'
    def __init__(self, targets, value):
        'constraints: value is splitable to len(targets) recursively'
        self.target = tuple(GName(n) for n in targets)
        self.value = value
    
    def __repr__(self):
        left = tuple(self.target) if len(self.target) > 1 else self.target[0]
        return str(left) + '=' + str(self.value)
    
class GFor(GBinding):
    def __init__(self, target, iterable):
        'constraints: iterable is, well, iterable'
        self.target = target
        self.value = iterable
    
    def __repr__(self):
        return 'for ' + str(self.target) + ' in ' + str(self.value)

class GWith(GBinding):
    def __init__(self, target, expr):
        'constraints: expr has attributes (__enter__, __exit__)'
        self.target = target
        self.value = expr
        
    def __repr__(self):
        return 'with ' + str(self.target) + ' as ' + str(self.value)
    
class GExcept(GBinding):
    def __init__(self, target, typename):
        '''constraints: target becomes typename
        (not subclass, since the user cannot know this)'''
        self.target = target
        self.value = typename
    
    def __repr__(self):
        return 'except ' + str(self.value) + ' as ' + str(self.target)
    
class GName(GraphNode):
    def __init__(self, node):
        self.name = node.id
        self.namespace = node.namespace
        self.id = (self.namespace, node.id)
    
    def __repr__(self):
        return str( ''.join(self.id) )

class GArg(GName):
    def __init__(self, node):
        node.id = node.arg
        super().__init__(node)
        self.pos = node.pos

    def __repr__(self):
        return super().__repr__() + '[{}]'.format(self.pos)

class GReturn(GraphNode):
    def __init__(self):
        self.tyoe = None

    def __repr__(self):
        return 'return'
   
class GExpression(GraphNode):
    def __init__(self, mytype):
        self.mytype = mytype

class GCall(GExpression):
    #TODO : add function-call type
    def __init__(self, func, args):
        self.func = func
        self.args = args
    
    def __repr__(self):
        return '{0}({1})'.format(self.func, ', '.join(str(i) for i in self.args))

class GTuple(GExpression):
    def __init__(self, t):
        self.tuplist = t

    def __eq__(self, other):
        return isinstance(other, GTuple) and self.tuplist == other.tuplist

    def __hash__(self):
        return hash(self.tuplist)
             
    def __repr__(self):
        return str(self.tuplist)

class GList(GTuple):
    def __repr__(self):
        return str(list(self.tuplist))

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
    def __init__(self, node):
        self.g = nx.DiGraph()
        self.ns = GlobalNamespace(node)
        self.ns.make_namespaces()
        self.build(self.ns)
        '''
        from bindfind import get_depth_lookups
        for namenode in get_depth_lookups(node):
            self.g.add_node(GName(namenode))
        '''
        
    def build(self, namespace):
        edges = []
        for name, node in namespace.locals:
            if isinstance(node, ast.arg):
                node.namespace = namespace.name
                gnode = GArg(node)
                #self.g.add_node(gnode)
            else:
                namenode = ast.Name(id=name, ctx=ast.Store())
                namenode.namespace = namespace.name
                gnode = GName(namenode)
            
            edge = (self.visit(node), gnode)
            self.g.add_edge(*edge) 
            edges.append(edge)
        for d in namespace.definitions:
            self.build(d)
            
        from definitions import Function
        if namespace.isfunction():
            from bindfind import iter_all_nodes
            rets = iter_all_nodes(namespace.node, lambda x : isinstance(x, ast.Return), 0)
            graph = nx.DiGraph(edges)
            retnode = GReturn()
            retnode.assign_node(namespace.node)
            for n in rets:
                graph.add_edge(self.visit(n), retnode)
            Function(namespace.node, graph, retnode)
         
    def printme(self):
        print([str(i) for i in self.g.nodes()])
        for i in self.g.edges():
            print(str(i))
        #self.visit(node)

    def visit_Name(self, node):
        return GName(node)
    
    def visit_ClassDef(self, node):
        res = GClassDef(node.name)
        res.assign_node(node)
        return res
    
    def visit_FunctionDef(self, node):
        from definitions import Function
        func = Function(node, self.g)
        res = GFunctionDef(node, func)
        res.assign_node(node)
        return res
    
    def visit_Call(self, node):
        "Call(func=Name(id='foo', ctx=Load()), args=[], keywords=[], starargs=None, kwargs=None)"
        func = self.visit(node.func)
        args = [self.visit(i) for i in node.args]
        res = GCall(func, args)
        res.assign_node(node)
        for v in [func] + args:
            self.g.add_edge(v, res)
        
        '''
        for keyword in node.keywords:
            keyword.value = self.visit(keyword.value)
        if isinstance(func, ast.Name):
            res = self.visit(func).call(node)
        elif isinstance(func, ast.Attribute):
            res = self.get_attr_types(func.value, func.attr).call(node)
            #if None in res:             print('recursive class definition found')
        return res
        '''
        return res
    
    def visit_Assign(self, node):
        value = self.visit(node.value)
        target = node.targets[0]
        if isinstance(target, ast.Name):
            return value
        if isinstance(target, ast.Tuple):
            #targets = [self.visit(i) for i in node.targets]
            res = GTupleAssign(target.elts, value)
            res.assign_node(node)
            self.g.add_edge(value, res)
            return res
        assert False
    
    def visit_For(self, node):
        iterable = self.visit(node.iter)
        res = GFor(self.visit(node.target), iterable)
        res.assign_node(node)
        self.g.add_edge(iterable, res)
        return res

    def visit_withitem(self, node):
        expr = self.visit(node.context_expr)
        res = GWith(expr, self.visit(node.optional_vars))
        res.assign_node(node)
        self.g.add_edge(expr, res)
        return res

    def visit_Num(self, value):
        types = { int : TT.INT, float : TT.FLOAT, complex : TT.COMPLEX }
        name = types[type(value.n)]
        t = TT.Specific.factory(name, value.n)
        return GNum(t)
    
    def visit_Str(self, node):
        return GStr(TT.TStr(node.s))
    
    def visit_Bytes(self, node):
        return GStr(TT.TStr(node.s))

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
        return GTuple(self.makeseq(node, TT.TTuple))

    def visit_List(self, node):
        return GList(self.makeseq(node, TT.LIST))
    
    def visit_Expr(self, node):
        return self.visit(node.value)
    
if __name__=='__main__':
    from ast import parse
    fp = parse(open('test.py').read())
    b = GraphCreator(fp)
    #b.build(fp)
    b.printme()
        
    
    