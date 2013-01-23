#!/sbin/python3

import ast
from typeset import Empty, Any
from types import *
from symtable import SymTable

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

class Globals:
    sym = SymTable()

class Expr:
    def __init__(self):
        pass
    
    def lookup(self, name):
        res = Globals.sym[name]
        if len(res) > 0:
            return res
        return Empty
     
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

    def Name(self, value):
        res = self.lookup(value.id)
        assert isinstance(res, TypeSet)
        if len(res)==0:
            return Empty
        return res
    
    def NameConstant(self, value):
        c = {None : NONE, False : BOOL, True : BOOL}
        return c[value.value]
    
    def get_attr_types(self, attr, this):
        return {i.dict[attr] for i in self.value_to_type(this) if attr in i.dict}
    
    def Attribute(self, value):
        res = self.get_attr_types(value.attr, value.value)
        if len(res)==0:
            return Empty
        return TypeSet(res)

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
    
    def value_to_type(self, value):
        assert isinstance(value, (ast.Num, ast.Str, ast.Dict, ast.Tuple, ast.List, ast.ListComp,
                                  ast.Name, ast.Call, ast.Attribute, ast.Bytes, ast.NameConstant))   
        v_type = type(value) 
        if v_type in Expr.typetofunc_single:
            res = st(Expr.typetofunc_single[v_type](self, value))
        elif v_type in Expr.typetofunc_multi:
            res = Expr.typetofunc_multi[v_type](self, value)
        else:
            print(value)
            res = st(Any)
        return res
    
    def ListComp(self, value):
        gen = value.generators[0]
        name = gen.target.id
        val = self.getseq(gen)
        assert val != []
        Globals.sym.push()
        for i in val:
            Globals.sym.update(name, i.typeset())
        vall = self.value_to_type(value.elt)
        Globals.sym.pop()
        res = TSeq.fromset(vall)
        assert not isinstance(res, TypeSet)
        return res
    
    typetofunc_single = {
                  ast.NameConstant : NameConstant,
                  ast.Num : Num,
                  ast.Str : Str,
                  ast.Bytes : Bytes,
                  ast.Dict : Dict,
                  ast.Tuple : Tuple,
                  ast.List : List,
                  ast.ListComp : ListComp
                  }
    typetofunc_multi = {
                  ast.Name : Name,
                  ast.Call : Call,
                  ast.Attribute : Attribute,
                  }
    
    def getseq(self, expr):
        return TypeSet({v for v in self.value_to_type(expr.iter) if augisinstance(v, TSeq)})
    
class Module:
    def __init__(self):
        self.sym = Globals.sym 
        self.expr = Expr()

    def import_module(self, module):
        self.sym = module.sym
        
    def do_assign(self, ass):
        val = self.expr.value_to_type(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                self.sym.update(target.id, val)
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in val if augisinstance(v, TSeq) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
                for name, objset in zip(target.elts, target_tuple):
                    self.sym.update(name.id, objset)

    def do_func(self, func):
        args = func.args
        defaults = [self.expr.value_to_type(i) for i in args.defaults]
        tup = (args.args, args.vararg, args.varargannotation, args.kwonlyargs, args.kwarg, args.kwargannotation, defaults, args.kw_defaults)
        #TODO : add type variables
        #TODO : support self-references through symtable
        self.sym.push()
        returns = self.run(func.body)
        self.sym.pop()
        res = TFunc(func.name, tup, returns)
        return func.name, res
    
    def do_class(self, cls):
        assert isinstance(cls, ast.ClassDef)
        #TODO : support self-references through symtable
        #assume for now that methods only calls previous ones
        c = TClass(cls.name, cls.bases, cls.keywords, cls.starargs, cls.kwargs)
        m = Module(cls.body, self)
        returns = m.run()
        c.update_namespace(m)
        assert len(returns)==0
        return cls.name, c
    
        
    def do_if(self, stat):
        return self.run(stat.body)
    
    def do_while(self, stat):
        while True:
            old_sym = repr(self.sym)
            ret = self.do_if(stat)
            new_sym = repr(self.sym)
            if old_sym == new_sym:
                return ret
    
    def do_for(self, stat):
        val = self.expr.getseq(stat)
        if len(val)==0:
            return Empty
        
        for i in val:
            self.sym.update(stat.target.id, i.typeset())
        return self.do_while(stat)
    
    def do_return(self, ret):
        return self.expr.value_to_type(ret.value)


    returnable = { 
            ast.For : do_for,
            ast.If : do_if,
            ast.While : do_while,
            ast.Return : do_return
    }
        
    def run(self, body):
        returns = TypeSet({})
        for stat in body:
            if isinstance(stat, ast.FunctionDef):
                fname, fobj = self.do_func(stat)
                self.sym.update_func(fname, fobj)
            elif isinstance(stat, ast.ClassDef):
                cname, cobj = self.do_class(stat)
                self.sym.update_func(cname, cobj)
            elif isinstance(stat, ast.Assign):
                self.do_assign(stat)
            elif type(stat) in Module.returnable:
                ret = Module.returnable[type(stat)](self, stat)
                returns.update(ret)
            elif isinstance(stat, ast.Expr):
                #assuming no side-effects for now
                pass 
            elif isinstance(stat, ast.Pass):
                pass
            else:
                print('unknown:', stat, stat.lineno, stat.value.s)
        if len(returns) > 0 and len(self.sym) == 1:
            print('top level return error')
        if len(returns) == 0 and len(self.sym) != 1:
            returns = st(NONE)
        assert isinstance(returns, TypeSet)
        return returns

def readfile(filename, module = None):
    return ast.parse(open(filename).read()).body

if __name__=='__main__':
    m = Module()
    #m.run(readfile('database/functions.py'))
    m.run(readfile('test/parsed.py'))
    print(m.sym)
    #print(*['{0} : {1}'.format(k,v) for k,v in m.sym.vars.items()], sep='\n')
    
