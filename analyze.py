#!/sbin/python3

import ast
from types import *

constants = {'None' : st(NONE), 'False' : st(TBool()), 'True' : st(TBool())}
funcs = {}
vartodic = {}

def updatedic(var_id, val):
    if var_id not in vartodic:
        vartodic[var_id] = TypeSet({})
    vartodic[var_id].update(val)

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

def get_restype(fname, args=[]):
    if fname in funcs:
        foo = funcs[fname]
        if not foo.ismatch(args):
            return st(Bottom)
        return funcs[fname].call(args)
    if fname in funcres:
        return st(funcres[fname])
        '''
    if fname in argfunc:
        return argfunc[fname](args)
        '''
    return st(Any)

class SingleHandlers:
    @staticmethod
    def Num(value):
        if isinstance(value.n, int):
            return INT
        elif isinstance(value.n, float):
            return FLOAT

    @staticmethod
    def Str(value):
        return STR

    @staticmethod
    def Dict(value):
        keys=[value_to_type(i) for i in value.keys]
        values=[value_to_type(i) for i in value.values]
        return TDict(keys,values)
    
    @staticmethod
    def Tuple(value):
        return TTuple([value_to_type(i) for i in value.elts])
        
    @staticmethod
    def List(value):
        return TList([value_to_type(i) for i in value.elts])

    @staticmethod
    def ListComp(value):
        name = value.generators[0].target.id
        val = getseq(value.generators[0])
        assert val != []
        save = None
        if name in vartodic:
            save = vartodic.get(name)
            del vartodic[name]
        for i in val:
            updatedic(name, i.typeset())
        vall = value_to_type(value.elt)
        if save != None:
            vartodic[name]= save
        res = TSeq.fromset(vall)
        assert not isinstance(res, TypeSet)
        return res

class MultiHandlers:
    @staticmethod
    def Name(value):
        res = TypeSet.union_all([d.get(value.id,TypeSet({})) for d in [constants, funcs, vartodic]])
        if len(res)==0:
            return st(Bottom)
        return res
    
    @staticmethod
    def get_attr_types(attr, this):
        return {i.dict[attr] for i in value_to_type(this) if attr in i.dict}
        
    @staticmethod
    def Call(value):
        args = [value_to_type(i) for i in value.args]
        func = value.func
        if isinstance(func, ast.Name):
            res = get_restype(func.id,  args)
        elif isinstance(func, ast.Attribute):
            acc = MultiHandlers.get_attr_types(func.attr, func.value)  
            res = TypeSet.union_all([foo(args) for foo in acc])
        assert isinstance(res, TypeSet)
        return res

    @staticmethod
    def Attribute(value):
        res = MultiHandlers.get_attr_types(value.attr, value.value)
        if len(res)==0:
            res = {Bottom}
        return TypeSet(res)
    
class Definitions:
           
    @staticmethod
    def FunctionDef(func):
        args = func.args
        defaults = [value_to_type(i) for i in args.defaults]
        tup = (args.args, args.vararg, args.varargannotation, args.kwonlyargs, args.kwarg, args.kwargannotation, defaults, args.kw_defaults)
        returns = value_to_type(func.body[0].value)
        f=TFunc(func.name, tup, returns)
        funcs[func.name] = f
        print(f)
        
'''
Module(body=[FunctionDef(name='foo', args=arguments(args=[], vararg=None, varargannotation=None, kwonlyargs=[], kwarg=None, kwargannotation=None, defaults=[], kw_defaults=[]),
                          body=[Return(value=NameConstant(value=None))], decorator_list=[], returns=None)])
'''                          
typetofunc_single = {
              ast.Num : SingleHandlers.Num,
              ast.Str : SingleHandlers.Str,
              ast.Dict : SingleHandlers.Dict,
              ast.Tuple : SingleHandlers.Tuple,
              ast.List : SingleHandlers.List,
              ast.ListComp : SingleHandlers.ListComp
              }
typetofunc_multi = {
              ast.Name : MultiHandlers.Name,
              ast.Call : MultiHandlers.Call,
              ast.Attribute : MultiHandlers.Attribute,
              }

def value_to_type(value):
    if type(value) in typetofunc_single:
        res = st(typetofunc_single[type(value)](value))
    elif type(value) in typetofunc_multi:
        res = typetofunc_multi[type(value)](value)     
    else:
        print(value)
        res = st(Any)
    return res

def do_assign(ass):
    target = ass.targets[0]
    val = value_to_type(ass.value)
    if isinstance(target, ast.Name):
        updatedic(target.id, val)
    elif isinstance(target, ast.Tuple):
        size = len(target.elts)
        target_matrix = [v.split_to(size) for v in val if augisinstance(v, TSeq) and v.can_split_to(size)]
        assert target_matrix != []
        target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
        for name, objset in zip(target.elts, target_tuple):
            updatedic(name.id, objset)
    
def getseq(expr):
    return TypeSet({v for v in value_to_type(expr.iter) if augisinstance(v, TSeq)})

def do_for(fstat):
    val = getseq(fstat)
    assert val != []
    for i in val:
        updatedic(fstat.target.id, i.typeset())

def walk(filename):
    s = list(ast.walk(ast.parse(open(filename).read())))
    for i in s:
        if isinstance(i, ast.Assign):
            do_assign(i)
        if isinstance(i, ast.For):
            do_for(i) 
        if isinstance(i, ast.FunctionDef):
            Definitions.FunctionDef(i)

    for i, j in funcs.items():
        print(i,': ', j)

    for i, j in vartodic.items():
        print(i,': ', j)

if __name__=='__main__':
    walk('database/functions.py')
    walk('test/parsed.py')
    
    
