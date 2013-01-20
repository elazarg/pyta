#!/sbin/python3

import ast
from database import *
from functools import reduce
filename = 'parsed.py'

vartodic = {'None' : {type(None)}}

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

def get_restype(fname, args=[]):
    if fname in funcres:
        return {funcres[fname]}
    if fname in argfunc:
        return argfunc[fname](args)
    return {Any}
    
def value_to_type(value):
    if isinstance(value, ast.Num):
        return {type(value.n)}
    if isinstance(value, ast.Str):
        return {str}
    if isinstance(value, ast.Dict):
        keys=[value_to_type(i) for i in value.keys]
        values=[value_to_type(i) for i in value.values]
        return {TDict(keys,values)}
    if isinstance(value, ast.Tuple):
        return {TTuple([value_to_type(i) for i in value.elts])}
    if isinstance(value, ast.List):
        return {TList([value_to_type(i) for i in value.elts])}
    if isinstance(value, ast.Name):
        if value.id not in vartodic:
            print("error: undefined reference to", value.id)
            return Bottom
        else:
            return vartodic[value.id]
    if isinstance(value, ast.Call):
        args = [value_to_type(i) for i in value.args]
        return get_restype(value.func.id,  args)   
    if isinstance(value, ast.ListComp):
        return do_listcomp(value)
    else:
        print(value)
        return Any

def updatedic(var_id, val):
    if var_id not in vartodic:
        vartodic[var_id] = set({})
    vartodic[var_id].update(val)
    if Any in vartodic[var_id]:
        vartodic[var_id]={Any}
    
def do_assign(ass):
    target = ass.targets[0]
    val = value_to_type(ass.value)
    if isinstance(target, ast.Name):
        updatedic(target.id, val)
    elif isinstance(target, ast.Tuple):
        size = len(target.elts)
        target_matrix = [v.split_to(size) for v in val if augisinstance(v, TSeq) and v.can_split_to(size)]
        assert target_matrix != []        
        target_tuple = [reduce(set.union,[v[i] for v in target_matrix]) for i in range(size)]
        for name, objset in zip(target.elts, target_tuple):
            updatedic(name.id, objset)
    
def getseq(expr):
    return {v for v in value_to_type(expr.iter) if augisinstance(v, TSeq)}

def do_for(fstat):
    val = getseq(fstat)
    assert val != []
    for i in val:
        updatedic(fstat.target.id, i.typeset())

def do_listcomp(expr):
    name = expr.generators[0].target.id
    val = getseq(expr.generators[0])
    assert val != []
    save = None
    if name in vartodic:
        save = vartodic.get(name)
        del vartodic[name]
    for i in val:
        updatedic(name, i.typeset())
    vall = value_to_type(expr.elt)
    if save != None:
        vartodic[name]= save
    return {TSeq.fromset(vall)}

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
