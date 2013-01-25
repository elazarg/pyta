'''
Created on Jan 25, 2013

@author: elazar

this module is application-independent
'''
from ast import *

def create_call(func, args):
    return Call(func, args, [], None, None)

def create_attr(left, attr, rarg):
    return create_call(Attribute(left, attr, Load()), [rarg])
    
def transform_subscript(sub):
    return create_attr(sub.value, '__getitem__', sub.slice.value)
    
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

def binop_to_method(op):
    assert isinstance(op, BinOp)
    opname = op_to_methodname(type(op.op))
    form = getformat(opname)
    attrname = form('')
    
    attr = create_attr(op.left, attrname, op.right)
    rattr = create_attr(op.right, form('r'), op.left)
    
    call = make_check_attr(op.left, attrname)
    
    return IfExp(test=call, body=attr, orelse=rattr)

def augassign_to_method(op):
    assert isinstance(op, AugAssign)
    opname = op_to_methodname(type(op.op))
    attrname = getformat(opname)('i')
    
    attr = create_attr(op.target, attrname, op.value)
    call = make_check_attr(op.target, attrname)
    binop = BinOp(op.target, op.op, op.value)
    ass = Assign(target=[op.target],value=binop)
    
    return If(test=call, body=[attr], orelse=[ass])

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

def test_binop():
    test(binop_to_method, ['1+2', '1*2','x*1','x*1'])

def test_augassign():
    test(augassign_to_method, ['x+=5'])
    
if __name__ == '__main__':
    test_augassign()

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