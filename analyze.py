#!/sbin/python3

'''
TODO:

* better ListComp (more specific)
* add binop support
* type variables
* augmented assignment
* better signature match
* single-valued-ints
* Exceptions

* better type-error warnings
* strict support for some sublanguage
* milestone - sit with Yuri/Eran

* attributes
* metaclasses

* less wild imports
* use visitors or something
* 

* basic control flow
* full CFG
*

* porting to c++ ?
* porting to datalog ?!
* some DSL
* basic framework
'''

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
        self.sym = Globals.sym
    
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
        res = self.sym[value.id]
        assert isinstance(res, TypeSet)
        if len(res)==0:
            return Empty
        return res
    
    def NameConstant(self, value):
        c = {None : NONE, False : BOOL, True : BOOL}
        return c[value.value]
    
    def get_attr_types(self, expr):
        return TypeSet.union_all({
                c.get_type_attr(expr.attr)
                for c in self.value_to_type(expr.value)
                if c.has_type_attr(expr.attr)})
    
    def Attribute(self, value):
        res = self.get_attr_types(value)
        if len(res)==0:
            return st(Empty)
        return res

    def Call(self, value):
        value.args = [self.value_to_type(i) for i in value.args]
        for keyword in value.keywords:
            keyword.value = self.value_to_type(keyword.value)
        func = value.func
        if isinstance(func, ast.Name):
            res = TypeSet.union_all([foo.call(value) for foo in self.value_to_type(func)
                                      if augisinstance(foo, TFunc) and foo.ismatch(value)])
        elif isinstance(func, ast.Attribute):
            acc = self.get_attr_types(func)
            res = TypeSet.union_all([foo.call(value) for foo in acc])
        assert isinstance(res, TypeSet)
        return res
    
    def value_to_type(self, value):
        assert isinstance(value, ast.expr)   
        v_type = type(value) 
        if v_type in Expr.typetofunc_single:
            res = st(Expr.typetofunc_single[v_type](self, value))
        elif v_type in Expr.typetofunc_multi:
            res = Expr.typetofunc_multi[v_type](self, value)
        else:
            print(value, 'of type', type(value))
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
    
    def Lambda(self, lmb):
        returns = self.value_to_type(lmb.body) 
        return self.create_func(lmb.args, returns, 'lambda')
    
    typetofunc_single = {
                  ast.NameConstant : NameConstant,
                  ast.Num : Num,
                  ast.Str : Str,
                  ast.Bytes : Bytes,
                  ast.Dict : Dict,
                  ast.Tuple : Tuple,
                  ast.List : List,
                  ast.ListComp : ListComp,
                  ast.Lambda : Lambda,
                  }
    typetofunc_multi = {
                  ast.Name : Name,
                  ast.Call : Call,
                  ast.Attribute : Attribute,
                  }
    
    def getseq(self, expr):
        return TypeSet({v for v in self.value_to_type(expr.iter) if augisinstance(v, TSeq)})
    
    def create_func(self, args, returns, t):
        args.defaults = [self.value_to_type(i) for i in args.defaults]
        args.kw_defaults = [(self.value_to_type(i) if i != None else i) for i in args.kw_defaults ]
        return TFunc(args, returns, t)
    
class Module:
    def __init__(self):
        self.sym = Globals.sym 
        self.expr = Expr()

    def Assign(self, ass):
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

    def Func(self, func):
        #TODO : add type variables
        #TODO : support self-references through symtable
        self.sym.push()
        returns = self.run(func.body)
        self.sym.pop()
        res = self.expr.create_func(func.args, returns, 'func')
        return func.name, res
    
    
    def Class(self, cls):
        assert isinstance(cls, ast.ClassDef)
        #assume for now that methods only calls previous ones
        c = TClass(cls.name, cls.bases, cls.keywords, cls.starargs, cls.kwargs)
        cur = {cls.name : st(c)}
        self.sym.push(cur)
        m.run(cls.body, False)
        temp = self.sym.pop()
        c.update_namespace(temp)
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
        
    def run(self, body, can_return = True):
        returns = TypeSet({})
        for stat in body:
            if isinstance(stat, ast.FunctionDef):
                fname, fobj = self.Func(stat)
                self.sym.update_func(fname, fobj)
            elif isinstance(stat, ast.ClassDef):
                cname, cobj = self.Class(stat)
                self.sym.update_func(cname, cobj)
            elif isinstance(stat, ast.Assign):
                self.Assign(stat)
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
        if len(returns) == 0 and len(self.sym) != 1 and can_return:
            returns = st(NONE)            
        assert isinstance(returns, TypeSet)
        return returns

def readfile(filename, module = None):
    return ast.parse(open(filename).read()).body

if __name__=='__main__':
    m = Module()
    #m.run(readfile('database/functions.py'))
    #m.run(readfile('database/Object.py'))
    m.run(readfile('test/parsed.py'))
    
    for i in m.sym.vars:
        for k,v in i.items():
            print('{0} : {1}'.format(k,v))
    #print(*['{0} : {1}'.format(k,v) for k,v in m.sym.vars.items()], sep='\n')
    
