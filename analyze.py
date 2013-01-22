#!/sbin/python3

import ast
from types import *

class SymTable:
    constants = {'None' : st(NONE), 'False' : st(BOOL), 'True' : st(BOOL)}
    
    def __init__(self):
        self.vars = {}

    def update(self, var_id, valset):
        if var_id not in self.vars:
            self.vars[var_id] = TypeSet({})
        self.vars[var_id].update(valset)

    def update_func(self, fname, func):
        if fname not in self.vars:
            self.vars[fname] = TypeSet({})
        self.vars[fname].add(func)
        
    def merge(self, other):
        assert isinstance(other, SymTable)
        for k,v in other.vars.items():
            self.update(k, v)
        
    def get_var(self, name):
        consts = SymTable.constants.get(name, TypeSet({}))
        return self.vars.get(name, TypeSet({})).union(consts)

    def __getitem__(self, name):
        return self.get_var(name)

    def __repr__(self):
        return '{0}'.format(repr(self.vars))
    
    def __eq__(self, other):
        return isinstance(other, SymTable) and self.vars == other.vars
    
    def __len__(self):
        return len(self.vars)
    
    def includes(self, other):
        return isinstance(other, SymTable) and all( (i,j) in self.vars.items() for i,j in other.vars.items())
    
def augisinstance(s, t):
    return s==Any or isinstance(s,t)

class Module:
    def lookup(self, name):
        res = self.sym[name]
        if len(res) > 0:
            return res
        if self.parent == None:
            return Empty
        return self.parent.lookup(name) 
        
    def Num(self, value):
        if isinstance(value.n, int):
            return INT
        elif isinstance(value.n, float):
            return FLOAT

    def Str(self, value):
        return STR

    def Bytes(self, value):
        return BYTES

    def Dict(self, value):
        keys=[self.value_to_type(i) for i in value.keys]
        values=[self.value_to_type(i) for i in value.values]
        return TDict(keys,values)
    
    def Tuple(self, value):
        return TTuple([self.value_to_type(i) for i in value.elts])
        
    def List(self, value):
        return TList([self.value_to_type(i) for i in value.elts])

    def ListComp(self, value):
        name = value.generators[0].target.id
        val = self.getseq(value.generators[0])
        assert val != []
        t_mod = Module(self)
        for i in val:
            t_mod.sym.update(name, i.typeset())
        vall = t_mod.value_to_type(value.elt)
        res = TSeq.fromset(vall)
        assert not isinstance(res, TypeSet)
        return res

    def Name(self, value):
        res = self.lookup(value.id)
        assert isinstance(res, TypeSet)
        if len(res)==0:
            return Empty
        return res
    
    def get_attr_types(self, attr, this):
        return {i.dict[attr] for i in self.value_to_type(this) if attr in i.dict}
    
    def Call(self, value):
        args = [self.value_to_type(i) for i in value.args]
        func = value.func
        if isinstance(func, ast.Name):
            allfuncs = [foo for foo in self.lookup(func.id)]
            res = TypeSet.union_all([foo.call(args) for foo in allfuncs
                                      if augisinstance(foo, TFunc) and foo.ismatch(args)])
        elif isinstance(func, ast.Attribute):
            acc = self.get_attr_types(func.attr, func.value)  
            res = TypeSet.union_all([foo(args) for foo in acc])
        assert isinstance(res, TypeSet)
        return res

    def Attribute(self, value):
        res = self.get_attr_types(value.attr, value.value)
        if len(res)==0:
            return Empty
        return TypeSet(res)

    def value_to_type(self, value):
        assert isinstance(value, (ast.Num, ast.Str, ast.Dict, ast.Tuple, ast.List, ast.ListComp,
                                  ast.Name, ast.Call, ast.Attribute, ast.Bytes))
        
        typetofunc_single = {
                      ast.Num : Module.Num,
                      ast.Str : Module.Str,
                      ast.Bytes : Module.Bytes,
                      ast.Dict : Module.Dict,
                      ast.Tuple : Module.Tuple,
                      ast.List : Module.List,
                      ast.ListComp : Module.ListComp
                      }
        typetofunc_multi = {
                      ast.Name : Module.Name,
                      ast.Call : Module.Call,
                      ast.Attribute : Module.Attribute,
                      }
        v_type = type(value) 
        if v_type in typetofunc_single:
            res = st(typetofunc_single[v_type](self, value))
        elif v_type in typetofunc_multi:
            res = typetofunc_multi[v_type](self, value)
        else:
            print(value)
            res = st(Any)
        return res
    
    def getseq(self, expr):
        return TypeSet({v for v in self.value_to_type(expr.iter) if augisinstance(v, TSeq)})

    def __init__(self, body, parent=None):
        self.body = body
        self.parent = parent
        self.sym = SymTable()

    def do_assign(self, ass):
        newsym = SymTable()
        val = self.value_to_type(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                newsym.update(target.id, val)
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in val if augisinstance(v, TSeq) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
                for name, objset in zip(target.elts, target_tuple):
                    newsym.update(name.id, objset)
        return newsym

    def do_func(self, func):
        args = func.args
        defaults = [self.value_to_type(i) for i in args.defaults]
        tup = (args.args, args.vararg, args.varargannotation, args.kwonlyargs, args.kwarg, args.kwargannotation, defaults, args.kw_defaults)
        #TODO : add type variables
        m = Module(func.body, self)
        returns = m.parse()
        res = TFunc(func.name, tup, returns)
        return func.name, res
    
    def do_for(self, stat):
        val = self.getseq(stat)
        assert val != []
        for i in val:
            self.sym.update(stat.target.id, i.typeset())
        m = Module(stat.body, self)
        returns = m.parse()
        return m.sym, returns
        
    def do_if(self, stat):
        m = Module(stat.body, self)
        returns = m.parse()
        return m.sym, returns
    
    def do_while(self, stat):
        returns = TypeSet({})
        while True:
            sym, ret = self.do_if(stat)
            print(sym)
            returns.update(ret)
            old_sym = repr(self.sym)
            self.sym.merge(sym)
            new_sym = repr(self.sym)
            if (old_sym==new_sym):
                break
        return sym, returns
    
    def do_return(self, ret):
        return self.value_to_type(ret.value)
    
    def parse(self):
        returns = TypeSet({})
        for stat in self.body:
            newreturn = TypeSet({})
            newsym = SymTable()
            if isinstance(stat, ast.Assign):
                newsym = self.do_assign(stat)
            elif isinstance(stat, ast.FunctionDef):
                fname, fobj = self.do_func(stat)
                self.sym.update_func(fname, fobj)
            elif isinstance(stat, ast.For):
                newsym, newreturn = self.do_for(stat)
            elif isinstance(stat, ast.If):
                newsym, newreturn = self.do_if(stat)
            elif isinstance(stat, ast.While):
                newsym, newreturn = self.do_while(stat)
            elif isinstance(stat, ast.Return):
                newreturn = self.do_return(stat)
            elif isinstance(stat, ast.Expr):
                pass #assuming no side-effects for now
            elif isinstance(stat, ast.Pass):
                pass
            else:
                print('unknown:', stat, stat.lineno, stat.value.s)
            self.sym.merge(newsym)
            returns.update(newreturn)
        if len(returns) > 0 and self.parent == None:
            print('top level return error')
        if len(returns) == 0 and self.parent != None:
            returns = st(NONE)
        assert isinstance(returns, TypeSet)
        return returns

def walk(filename, module = None):
    f_ast = ast.parse(open(filename).read())
    m=Module(f_ast.body, module)
    m.parse()
    return m

if __name__=='__main__':
    m = walk('test/parsed.py', walk('database/functions.py'))
    print(*['{0} : {1}'.format(k,v) for k,v in m.sym.vars.items()], sep='\n')
    
