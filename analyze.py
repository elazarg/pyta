#!/sbin/python3

import ast
from types import *
filename = 'parsed.py'

vartodic = {'None' : TypeSet({NONE}) }

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

def get_restype(fname, args=[]):
    if fname in funcres:
        return st(funcres[fname])
    if fname in argfunc:
        return argfunc[fname](args)
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
        if value.id not in vartodic:
            print("error: undefined reference to", value.id)
            return st(Bottom)
        else:
            return vartodic[value.id]

    @staticmethod
    def Call(value):
        args = [value_to_type(i) for i in value.args]
        if isinstance(value.func, ast.Name):
            res = get_restype(value.func.id,  args)
        elif isinstance(value.func, ast.Attribute):
            caller = value.func.value
            attr = value.func.attr 
            res = TypeSet.union_all([i.dict[attr](args) for i in value_to_type(caller) if attr in i.dict]).types
        return res

    @staticmethod
    def Attribute(value):
        res = {i.dict[value.attr] for i in value_to_type(value.value) if value.attr in i.dict}
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

def value_to_type(value):
    if type(value) in typetofunc_single:
        res = st(typetofunc_single[type(value)](value))
    elif type(value) in typetofunc_multi:
        res = typetofunc_multi[type(value)](value)     
    else:
        print(value)
        res = st(Any)
    return res

def updatedic(var_id, val):
    if var_id not in vartodic:
        vartodic[var_id] = TypeSet({})
    vartodic[var_id].update(val)
    
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

if __name__ == '__main__':
    s = list(ast.walk(ast.parse(open(filename).read())))
    for i in s:
        if isinstance(i, ast.Assign):
            do_assign(i)
        if isinstance(i, ast.For):
            do_for(i) 
    
    del vartodic['None']
    for i, j in vartodic.items():
        print(i,': ', j)
