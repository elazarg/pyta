'''
Created on Jan 25, 2013

@author: elazar

this module is application-independent
'''
from ast import *

def create_call(func, args):
    return Call(func, args, [], None, None)

def create_attr(left, attr, *rarg):
    return create_call(Attribute(left, attr, Load()), list(rarg))

def op_to_methodname(op):
    ops = {Add : 'add', And : 'and', BitAnd : 'bitand', BitOr : 'bitor', BitXor : 'bitxor',
           Eq : 'eq', Gt : 'gt', GtE : 'gte', Lt : 'lt', LtE : 'lte',
           In : 'contains', Invert : 'invert',  Pow : 'pow', RShift : 'rshift', 
           Mod : 'mod', Mult : 'mul',   Div : 'truediv', FloorDiv : 'floordiv', 
           LShift : 'lshift', Sub : 'sub', UAdd : 'uadd', USub : 'usub'}
    others = [NotIn, NotEq, Compare, DictComp, SetComp,  UnaryOp] 
    return ops[op]

def getformat(opname):
    return lambda pref : '__{0}{1}__'.format(pref, opname)

def make_check_attr(left, attrname):
    return create_call(func=Name('hasattr', Load()),  args=[left, Str(attrname)])

['AST', 'Add', 'And', 'Assert', 'Assign', 'Attribute', 'AugAssign', 'AugLoad', 'AugStore', 'BinOp', 'BitAnd', 'BitOr', 'BitXor', 'BoolOp', 'Break', 'Bytes', 'Call', 'ClassDef', 'Compare', 'Continue', 'Del', 'Delete', 'Dict', 'DictComp', 'Div', 'Ellipsis', 'Eq', 'ExceptHandler', 'Expr', 'Expression', 'ExtSlice', 'FloorDiv', 'For', 'FunctionDef', 'GeneratorExp', 'Global', 'Gt', 'GtE', 'If', 'IfExp', 'Import', 'ImportFrom', 'In', 'Index', 'Interactive', 'Invert', 'Is', 'IsNot', 'LShift', 'Lambda', 'List', 'ListComp', 'Load', 'Lt', 'LtE', 'Mod', 'Module', 'Mult', 'Name', 'NodeTransformer', 'NodeVisitor', 'Nonlocal', 'Not', 'NotEq', 'NotIn', 'Num', 'Or', 'Param', 'Pass', 'Pow', 'PyCF_ONLY_AST', 'RShift', 'Raise', 'Return', 'Set', 'SetComp', 'Slice', 'Starred', 'Store', 'Str', 'Sub', 'Subscript', 'Suite', 'TryExcept', 'TryFinally', 'Tuple', 'UAdd', 'USub', 'UnaryOp', 'While', 'With', 'Yield', '__builtins__', '__cached__', '__doc__', '__file__', '__name__', '__package__', '__version__', 'alias', 'arg', 'arguments', 'boolop', 'cmpop', 'comprehension', 'copy_location', 'dump', 'excepthandler', 'expr', 'expr_context', 'fix_missing_locations', 'get_docstring', 'increment_lineno', 'iter_child_nodes', 'iter_fields', 'keyword', 'literal_eval', 'mod', 'operator', 'parse', 'slice', 'stmt', 'unaryop', 'walk']

def maketest(func):
    def wr(text):
        x=parse(text).body[0]
        if isinstance(x, Expr):
            x=x.value
        res = func(x)
        print(dump(res))
    return wr

def test(func, cases):
    test = maketest(func)
    for case in cases:
        test(case)

def mutator(method):
    def wr(self, node):
        res = method(self, node)
        if res != node:
            self.changed = True
        return res
    return wr


flow_stoppers = (Return, Break, Continue) 

class Transformer(NodeTransformer):

    def take_upto(self, body, stopper=lambda x: isinstance(x, flow_stoppers), ifempty=Pass()):
        def upto():
            for stmt in body:
                res = self.visit(stmt)
                if res is not None:
                    yield res
                if stopper(stmt):
                    return
        res = list(upto())
        if ifempty is not None and res == []:
            res = [ifempty]
        body[:]=res

    def __init__(self):
        super().__init__()
        self.changed = True
        
    def has_changed(self):
        res = self.changed
        self.changed = False
        return res

    @mutator
    def visit_AugAssign(self, op):
        opname = op_to_methodname(type(op.op))
        attrname = getformat(opname)('i')
        
        attr = create_attr(op.target, attrname, op.value)
        call = make_check_attr(op.target, attrname)
        binop = BinOp(op.target, op.op, op.value)
        ass = Assign(targets=[op.target], value=binop)
        
        return If(test=call, body=[attr], orelse=[ass])

    @mutator
    def visit_Subscript(self, sub):
        s = sub.slice
        if isinstance(s, Index):
            return create_attr(sub.value, '__getitem__', s.value)
        else:
            args = [k if k else NameConstant(k) for k in [s.lower, s.upper, s.step]]
            call = create_call('__builtins__.slice', args)
            return create_attr(sub.value, '__getitem__', call)
    
    @mutator
    def visit_BinOp(self, binop):
        opname = op_to_methodname(type(binop.op))
        form = getformat(opname)
        attrname = form('')
        
        attr = create_attr(binop.left, attrname, binop.right)
        rattr = create_attr(binop.right, form('r'), binop.left)
        
        call = make_check_attr(binop.left, attrname)
        
        return IfExp(test=call, body=attr, orelse=rattr)

    @mutator
    def visit_Return(self, ret):
        if ret.value is None:
            ret.value = NameConstant(value=None)
        return ret

    @mutator
    def visit_FunctionDef(self, node):
        self.take_upto(node.body, ifempty=Return(NameConstant(None)))
        return node

    @mutator
    def visit_body(self, node):
        self.take_upto(node.body)
        return node
    
    visit_ClassDef = visit_body
    visit_ExceptHandler = visit_body
    
    @mutator
    def visit_body_orelse(self, node):
        self.take_upto(node.body)
        self.take_upto(node.orelse, ifempty=None)
        return node
    
    visit_If = visit_body_orelse
    visit_While = visit_body_orelse
    visit_For = visit_body_orelse
    visit_With = visit_body_orelse
      
    @mutator
    def visit_Try(self, node):
        self.visit_body_orelse(node)
        
        stopper = lambda x: isinstance(x.type, (type(None), Ellipsis))
        ifempty = None if node.finalbody != [] else Pass() 
        self.take_upto(node.handlers, stopper, ifempty)
        
        if node.finalbody:
            self.take_upto(node.finalbody)
        return node
      
    @mutator
    def visit_Pass(self, node):
        return None
    
def trans(root):
    x = Transformer()
    #while x.has_changed():
    x.visit(root)
    for n in iter_child_nodes(root):
        trans(n)
    #print(to_source(root))
    return root
    
from codegen import to_source
if __name__ == '__main__':
    p = parse(open('test.py').read())
    trans(p)
    st = to_source(p)
    print(st)
    
'''
x.__lt__(y) <==> x<y
x.__lshift__(y) <==> x<<y
x.__invert__() <==> ~x
x.__le__(y) <==> x<=y
x.__rlshift__(y) <==> y<<x
x.__lt__(y) <==> x<y
x.__lshift__(y) <==> x<<y
x.__invert__() <==> ~x
x.__le__(y) <==> x<=y
x.__rlshift__(y) <==> y<<x
x.__eq__(y) <==> x==y
x.__rshift__(y) <==> x>>y
x.__ne__(y) <==> x!=y
x.__rrshift__(y) <==> y>>x
x.__gt__(y) <==> x>y
x.__and__(y) <==> x&y
x.__ge__(y) <==> x>=y
x.__rand__(y) <==> y&x
x.__add__(y) <==> x+y
x.__xor__(y) <==> x^y
x.__radd__(y) <==> y+x
x.__rxor__(y) <==> y^x
x.__sub__(y) <==> x-y
x.__or__(y) <==> x|y
x.__rsub__(y) <==> y-x
x.__ror__(y) <==> y|x
x.__mul__(y) <==> x*y
x.__rmul__(y) <==> y*x
x.__float__() <==> float(x)
x.__mod__(y) <==> x%y
x.__floordiv__(y) <==> x//y
x.__rmod__(y) <==> y%x
x.__rfloordiv__(y) <==> y//x
x.__eq__(y) <==> x==y
x.__rshift__(y) <==> x>>y
x.__ne__(y) <==> x!=y
x.__rrshift__(y) <==> y>>x
x.__gt__(y) <==> x>y
x.__and__(y) <==> x&y
x.__ge__(y) <==> x>=y
x.__rand__(y) <==> y&x
x.__add__(y) <==> x+y
x.__xor__(y) <==> x^y
x.__radd__(y) <==> y+x
x.__rxor__(y) <==> y^x
x.__sub__(y) <==> x-y
x.__or__(y) <==> x|y
T.__new__(S, ...) -> a new object with type S, a subtype of T
x.__rsub__(y) <==> y-x
x.__ror__(y) <==> y|x
x.__mul__(y) <==> x*y
x.__rmul__(y) <==> y*x
x.__float__() <==> float(x)
x.__mod__(y) <==> x%y
x.__floordiv__(y) <==> x//y
x.__rmod__(y) <==> y%x
x.__rfloordiv__(y) <==> y//x
x.__divmod__(y) <==> divmod(x, y)
x.__rdivmod__(y) <==> divmod(y, x)
x.__rtruediv__(y) <==> y/x
x.__pow__(y[, z]) <==> pow(x, y[, z])
x[y:z] <==> x[y.__index__():z.__index__()]
y.__rpow__(x[, z]) <==> pow(x, y[, z])

'''