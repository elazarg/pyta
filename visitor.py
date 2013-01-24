#!/sbin/python3
import ast
from typeset import TypeSet, Empty, Any, st
from types import TObject, TTuple, TList, TSeq, TDict
from types import NONE, BOOL, INT, STR, BYTES, FLOAT, COMPLEX
from definitions import TArguments, TFunc, TClass
from symtable import SymTable

def augisinstance(s, t):
    return s==Any or isinstance(s,t)

def singletype(method):
    def wr(self, node):
        t = method(self, node)
        if not issubclass(type(t), TObject):
            print(method)
            print(t)
            assert False
        return st(t)
    return wr

class Visitor(ast.NodeVisitor):
    def generic_visit(self, node):
        print(ast.dump(node))
        for n in ast.iter_child_nodes(node):
            self.visit(n)
    
    def __init__(self, parent = None):
        self.sym = SymTable()
        self.parent = parent
        self.returns = None
        
    def get_returns(self):
        return self.returns
    
    def lookup(self, name):
        res = self.sym.get_var(name, None)
        if self.parent and res == None:
            return self.parent.lookup(name)
        return res
    
    def bind_weak(self, var_id, typeset):
        return self.sym.bind(var_id, typeset)
    
    def print(self):
        self.sym.print()
        
    def visit_Assign(self, ass):
        typeset = self.visit(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                self.bind_weak(target.id, typeset) 
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in typeset if augisinstance(v, TSeq) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
                for name, typeset2 in zip(target.elts, target_tuple):
                    self.bind_weak(name.id, typeset2)

    def visit_all_childs(self, node):
        for n in ast.iter_child_nodes(node):
            self.visit(n)
        return self.get_returns()

    def visit_FunctionDef(self, func):
        #TODO : add type variables
        #TODO : support self-references through symtable
        v = Visitor(self)
        returns = v.visit_run(func)
        res = self.create_func(func.args, returns, 'func')
        self.bind_weak(func.name, st(res))
    
    def visit_ClassDef(self, cls):
        #assume for now that methods only calls previous ones
        #tofix: contaminating global namespace 
        c = TClass(cls.name, cls.bases, cls.keywords, cls.starargs, cls.kwargs)
        cur = (cls.name, st(c))
        v = Visitor(self)
        returns = v.visit_run(cls)
        if returns != None:
            print('cannot return from class definition')
        temp = v.sym
        c.update_namespace(temp)
        self.bind_weak(*cur)
        
    def visit_If(self, stat):
        return self.visit_all_childs(stat)
    
    def go_round(self, node):
        #TODO : better comparison
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
        val = self.getseq(stat)
        if len(val)==0:
            return
        for i in val:
            self.bind_weak(stat.target.id, i.typeset())
        #TODO : finite repeats where possible
        return self.visit_While(stat)
    
    def visit_Return(self, ret):
        return self.visit(ret.value)

    def visit_Pass(self, ps):
        pass

    def visit_run(self, node):
        return_values = TypeSet({})
        for n in node.body:
            ret = self.visit(n)
            if ret != None:
                return_values.update(ret)
        assert isinstance(return_values, TypeSet)
        if len(return_values) > 0:
            return return_values

    def visit_Module(self, node):
        return self.visit_run(node)
    
    @singletype
    def visit_Num(self, value):
        types = { int : INT, float : FLOAT, complex : COMPLEX }
        res = types.get(type(value.n))
        if res == None:
            print('unknown Num:', ast.dump(value))
        return res
    
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
        res = self.lookup(value.id)
        if res == None:
            res = TypeSet({})
        assert isinstance(res, TypeSet)
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

    @singletype
    def visit_ListComp(self, value):
        gen = value.generators[0]
        name = gen.target.id
        val = self.getseq(gen)
        assert val != []
        v = Visitor(self)
        for i in val:
            v.bind_weak(name, i.typeset())
        vall = v.visit(value.elt)
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


if __name__=='__main__':
    import analyze
    analyze.main()