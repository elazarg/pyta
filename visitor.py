#!/sbin/python3
import ast
from typeset import Empty, Any
from types import *
from symtable import SymTable

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

def singletype(method):
    return lambda self, node : st(method(self, node))

class TClass(TObject):
    def __init__(self, name, bases, keywords, starargs, kwargs):
        self.name, self.bases = name, bases
        self.keywords, self.starargs, self.kwargs = keywords, starargs, kwargs
        self.namespace = SymTable()
        
    def update_namespace(self, sym):
        self.namespace.merge(sym)
    
    def __repr__(self):
        return 'Class: {0}'.format(self.name)
    
    def get_type_attr(self, name):
        return self.namespace.get_var(name) 
    
    def has_type_attr(self, name):
        return len(self.namespace.get_var(name)) > 0 
    
    def call(self, args):
        return st(self)


class Visitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print(ast.dump(node))
        for n in ast.iter_child_nodes(node):
            self.visit(n)
    
    def __init__(self, parent = None):
        self.sym = SymTable() 
        self.expr = self
        self.returns = TypeSet({})
        
    def get_returns(self):
        return self.returns

    def visit_Assign(self, ass):
        val = self.visit(ass.value)
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

    def visit_all_childs(self, node):
        for n in ast.iter_child_nodes(node):
            self.visit(n)
        return self.get_returns()

    def visit_FunctionDef(self, func):
        #TODO : add type variables
        #TODO : support self-references through symtable
        v = Visitor(self)
        returns = v.visit_all_childs(func)
        res = self.create_func(func.args, returns, 'func')
        self.sym.update(func.name, st(res))
    
    def visit_ClassDef(self, cls):
        #assume for now that methods only calls previous ones
        #tofix: contaminating global namespace 
        c = TClass(cls.name, cls.bases, cls.keywords, cls.starargs, cls.kwargs)
        cur = (cls.name, st(c))
        v = Visitor(self)
        returns = v.visit_all_childs(cls)
        if returns != None:
            print('cannot return from class definition')
        temp = v.sym
        c.update_namespace(temp)
        self.sym.update(*cur)
        
    def visit_If(self, stat):
        return self.visit_all_childs(stat)
    
    def go_round(self, node):
        old_sym = repr(self.sym)
        ret = self.visit_all_childs(node)
        new_sym = repr(self.sym)
        return ret, old_sym == new_sym
    
    def visit_While(self, stat):
        while True:
            ret, done = self.go_round(stat)
            if done:
                return ret
    
    def visit_For(self, stat):
        val = self.expr.getseq(stat)
        if len(val)==0:
            return
        for i in val:
            self.sym.update(stat.target.id, i.typeset())
        #TODO : finite repeats where possible
        return self.visit_While(stat)
    
    def visit_Return(self, ret):
        res = self.visit(ret.value)
        self.returns.update(res)
        return res

    def visit_Module(self, node, can_return = True):
        returns = TypeSet({})
        for n in ast.iter_child_nodes(node):
            ret = self.visit(n)
            if ret != None:
                returns.update(ret)
        if len(returns) == 0 and len(self.sym) != 1 and can_return:
            returns = st(NONE)            
        assert isinstance(returns, TypeSet)
        self.returns = returns 
        return returns
    
    @singletype
    def visit_Num(self, value):
        if isinstance(value.n, int):
            return INT
        elif isinstance(value.n, float):
            return FLOAT

    @singletype
    def visit_Str(self, value):
        return STR
    
    @singletype
    def visit_Bytes(self, value):
        return BYTES

    @singletype
    def visit_Dict(self, value):
        keys=[self.visit(i) for i in value.keys]
        values=[self.visit(i) for i in value.values]
        return TDict(keys,values)

    @singletype    
    def visit_Tuple(self, value):
        return TTuple([self.visit(i) for i in value.elts])
        
    @singletype
    def visit_List(self, value):
        return TList([self.visit(i) for i in value.elts])

    def visit_Name(self, value):
        res = self.sym[value.id]
        assert isinstance(res, TypeSet)
        if len(res)==0:
            return Empty
        return res
    
    @singletype
    def visit_NameConstant(self, value):
        c = {None : NONE, False : BOOL, True : BOOL}
        return c[value.value]
    
    def get_attr_types(self, expr):
        return TypeSet.union_all({
                c.get_type_attr(expr.attr)
                for c in self.visit(expr.value)
                if c.has_type_attr(expr.attr)})
    
    def visit_Attribute(self, value):
        res = self.get_attr_types(value)
        if len(res)==0:
            return st(Empty)
        return res

    def visit_Call(self, value):
        value.args = [self.visit(i) for i in value.args]
        for keyword in value.keywords:
            keyword.value = self.visit(keyword.value)
        func = value.func
        if isinstance(func, ast.Name):
            res = TypeSet.union_all([foo.call(value) for foo in self.visit(func)
                                      if augisinstance(foo, TFunc) and foo.ismatch(value)])
        elif isinstance(func, ast.Attribute):
            acc = self.get_attr_types(func)
            res = TypeSet.union_all([foo.call(value) for foo in acc])
        assert isinstance(res, TypeSet)
        return res

    '''    
    def visit(self, value):
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
    ''' 
    @singletype
    def visit_ListComp(self, value):
        gen = value.generators[0]
        name = gen.target.id
        val = self.getseq(gen)
        assert val != []
        self.sym.push()
        for i in val:
            self.sym.update(name, i.typeset())
        vall = self.visit(value.elt)
        self.sym.pop()
        res = TSeq.fromset(vall)
        assert not isinstance(res, TypeSet)
        return res
    
    @singletype
    def visit_Lambda(self, lmb):
        returns = self.visit(lmb.body) 
        return self.create_func(lmb.args, returns, 'lambda')

    def visit_Expr(self, expr):
        for n in ast.iter_child_nodes(expr):
            self.visit(n)
    
    def visit_arguments(self, args):
        return TArguments(args)
        
    def getseq(self, expr):
        return TypeSet({v for v in self.visit(expr.iter) if augisinstance(v, TSeq)})
    
    def create_func(self, args, returns, t):
        args.defaults = [self.visit(i) for i in args.defaults]
        args.kw_defaults = [(self.visit(i) if i != None else i) for i in args.kw_defaults ]
        return TFunc(args, returns, t)

def readfile(filename, module = None):
    return ast.parse(open(filename).read())


if __name__=='__main__':
    v = Visitor()
    #m.run(readfile('database/functions.py'))
    #m.run(readfile('database/Object.py'))
    v.visit(readfile('test/parsed.py'))
    
    for i in v.sym.vars:
        for k,v in i.items():
            print('{0} : {1}'.format(k,v))    