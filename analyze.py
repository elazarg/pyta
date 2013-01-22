#!/sbin/python3

import ast
from types import *

funcs = {}
vartodic = {}
constants = {'None' : st(NONE), 'False' : st(TBool()), 'True' : st(TBool())}

class SymTable:
    constants = {'None' : st(NONE), 'False' : st(TBool()), 'True' : st(TBool())}
    
    def __init__(self):
        self.funcs = {}
        self.vars = {}

    def update(self, var_id, valset):
        if var_id not in self.vars:
            self.vars[var_id] = TypeSet({})
        self.vars[var_id].update(valset)

    def get_func(self, name):
        return self.funcs.get(name, TypeSet({}))

    def get_var(self, name):
        return self.vars.get(name, TypeSet({})).union(SymTable.constants)

    def __getitem__(self, name):
        return self.get_var(name).union(self.get_func(name))

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

def getseq(expr):
    return TypeSet({v for v in value_to_type(expr.iter) if augisinstance(v, TSeq)})


def value_to_type(value):
    if type(value) in typetofunc_single:
        res = st(typetofunc_single[type(value)](value))
    elif type(value) in typetofunc_multi:
        res = typetofunc_multi[type(value)](value)     
    else:
        print(value)
        res = st(Any)
    return res

class Module:
    def __init__(self, ast_module, parent=None):
        self.module = ast_module
        self.parent = parent
        self.parse(self.module.body)
    
    def do_assign(self, ass):
        val = value_to_type(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                updatedic(target.id, val)
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in val if augisinstance(v, TSeq) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
                for name, objset in zip(target.elts, target_tuple):
                    updatedic(name.id, objset)

    def do_func(self, func):
        args = func.args
        defaults = [value_to_type(i) for i in args.defaults]
        tup = (args.args, args.vararg, args.varargannotation, args.kwonlyargs, args.kwarg, args.kwargannotation, defaults, args.kw_defaults)
        returns = value_to_type(func.body[0].value)
        f=TFunc(func.name, tup, returns)
        funcs[func.name] = f
    
    def do_for(self, forstat):
        val = getseq(forstat)
        assert val != []
        for i in val:
            updatedic(forstat.target.id, i.typeset())
        return self.parse(forstat.body)
        
    def do_if(self, ifstat):
        return self.parse(ifstat.body)
    
    def parse(self, body):
        for stat in body:
            if isinstance(stat, ast.Assign):
                self.do_assign(stat)
            elif isinstance(stat, ast.FunctionDef):
                self.do_func(stat)
            elif isinstance(stat, ast.For):
                self.do_for(stat)
            elif isinstance(stat, (ast.If, ast.While)):
                self.do_if(stat)
            elif isinstance(stat, ast.Return):
                self.do_for(stat)                
            elif isinstance(stat, ast.Expr):
                pass #assuming no side-effects for now
            else:
                print('unknown:', stat, stat.lineno, stat.value.s)

def walk(filename):
    f_ast = ast.parse(open(filename).read())
    Module(f_ast)

    for i, j in funcs.items():
        print(i,': ', j)

    for i, j in vartodic.items():
        print(i,': ', j)

if __name__=='__main__':
    walk('database/functions.py')
    walk('test/parsed.py')
    
    
