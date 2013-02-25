#!/sbin/python3
import ast 
from types import TypeSet, Class, ANY, TYPE, st
from types import BOOL, INT, FLOAT, NONE, COMPLEX
from types import BYTES, STR, TUPLE, LIST, SEQ, DICT
from definitions import Function, Arguments
from symtable import SymTable

def augisinstance(s, t): 
    return s==ANY or isinstance(s,t)

def singletype(method):
    def wr(self, node):
        t = method(self, node)
        if type(t) is TypeSet:
            print(method)
            print(t)
            assert False
        return st(t)
    return wr

def visit_result(method):
    def wrapped(self, args):
        #ast.dump(args)
        res = method(self, args)
        assert issubclass(type(res), ast.AST)
        return self.visit(res)
    return wrapped

class Visitor(ast.NodeVisitor):
    
    def generic_visit(self, node):
        print(ast.dump(node))
        for n in ast.iter_child_nodes(node):
            self.visit(n)
    
    def __init__(self, parent = None):
        if parent != None:
            self.sym = SymTable(parent.sym)
        else:
            self.sym = SymTable()
        self.parent = parent
        
        if parent == None:
            self.bind_weak('NoneType', st(NONE))
            d = {'int' : INT, 'bool' : BOOL, 'float' : FLOAT, 'complex' : COMPLEX}
            for k, v in d.items(): 
                self.bind_weak(k, st(v))
    
    def lookup(self, name):
        res = self.sym.get_var(name)
        '''
        if self.parent and res == None:
            return self.parent.lookup(name)
        '''
        return res
    
    def bind_weak(self, var_id, TypeSet):
        return self.sym.bind(var_id, TypeSet)
    
    def print(self):
        self.sym.print()
    
    def visit_AugAssign(self, ass):
        assert False
        
    def visit_Assign(self, ass):
        TypeSet = self.visit(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                self.bind_weak(target.id, TypeSet) 
            elif isinstance(target, ast.Attribute):
                for t in self.visit(target.value):
                    t.weak_bind(target.value.id, TypeSet)
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in TypeSet if augisinstance(v, SEQ) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [TypeSet.union_all([v[i] for v in target_matrix]) for i in range(size)]
                for name, TypeSet2 in zip(target.elts, target_tuple):
                    self.bind_weak(name.id, TypeSet2)
            else:
                assert False

    def visit_all_childs(self, node):
        returns = TypeSet({})
        for n in ast.iter_child_nodes(node):
            res = self.visit(n)
            if isinstance(n, ast.stmt) and res != None:
                returns.update(res)
        return returns
    
    def get_attr_types(self, value, name):
        seq = self.visit(value)
        #print(seq)
        seq1 = [c for c in seq if c.has_type_attr(name)]
        #print(seq1)
        return TypeSet.union_all({
                c.get_type_attr(name)
                for c in seq1})
    
    def visit_Attribute(self, attr):
        return self.get_attr_types(attr.value, attr.attr)

    def visit_FunctionDef(self, func):
        #TODO : add type variables
        #TODO : support self-references through symtable
        v = Visitor(self)
        returns = v.run(func)
        if len(returns)==0:
            returns = self.lookup('NoneType')
        res = self.create_func(func.args, returns, 'func')
        self.bind_weak(func.name, st(res))
    
    def visit_ClassDef(self, cls):
        #assume for now that methods only calls previous ones
        v = Visitor(self)
        returns = v.run(cls)
        if returns:
            print('cannot return from class definition')

        c = Class(cls.name, v.sym, cls)
        cur = (cls.name, st(c))
        
        builtins = {'float', 'complex', 'int'}
        if cls.name in builtins:
            self.lookup(cls.name).readjust(cur[1])
        self.bind_weak(*cur)
            
    def visit_Call(self, value):
        value.args = [self.visit(i) for i in value.args]
        for keyword in value.keywords:
            keyword.value = self.visit(keyword.value)
        func = value.func
        if isinstance(func, ast.Name):
            res = TypeSet.union_all([foo.call(value)
                                      for foo in self.visit(func)
                                      if foo.ismatch(value)])
        elif isinstance(func, ast.Attribute):
            collect = [foo.call(value) for foo in self.get_attr_types(func.value, func.attr)
                                     if foo != None and foo.ismatch(value)]
            if None in collect:
                print('recursive class definition found')
            res = TypeSet.union_all([foo.call(value)
                                     for foo in self.get_attr_types(func.value, func.attr)
                                     if foo != None and foo.ismatch(value)])
        assert isinstance(res, TypeSet)
        return res
            
    def visit_IfExp(self, ifexp):
        r1 = self.visit(ifexp.body)
        r2 = self.visit(ifexp.orelse)
        res = r1.union(r2)
        return res
    
    def visit_Subscript(self, sub):
        assert False

    def visit_BinOp(self, binop):
        assert False
    
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
            self.bind_weak(stat.target.id, i.TypeSet())
        #TODO : finite repeats where possible
        return self.visit_While(stat)
    
    def visit_Return(self, ret):
        if ret.value == None:
            res = self.lookup('NoneType')
        else:
            res = self.visit(ret.value)
            #assert len(res)>0
        return res

    def run(self, node):
        return_values = TypeSet({})
        for n in node.body:
            ret = self.visit(n)
            if ret != None:
                return_values.update(ret)
        assert isinstance(return_values, TypeSet)
        #if len(return_values) > 0:
        return return_values

    def visit_Module(self, node):
        return self.run(node)
      
    def visit_Num(self, value):
        types = { int : 'int', float : 'float', complex : 'complex' }
        name = types.get(type(value.n))
        if name == None:
            print('unknown Num:', ast.dump(value))
            return None
        res = TypeSet({i.new_instance('int object', None) for i in self.lookup(name)})
        
        assert len(res) > 0
        for i in res:
            i.value = value.n
        return res
    
    def visit_Str(self, value):
        return STR
    
    def visit_Bytes(self, value):
        return BYTES

    def visit_Dict(self, value):
        keys=[self.visit(i) for i in value.keys]
        values=[self.visit(i) for i in value.values]
        return DICT(keys,values)

    def visit_Tuple(self, value):
        return TUPLE([self.visit(i) for i in value.elts])
        
    def visit_List(self, value):
        return LIST([self.visit(i) for i in value.elts])

    def visit_Name(self, value):
        res = self.lookup(value.id)
        if res == None:
            res = TypeSet({})
        assert isinstance(res, TypeSet)
        return res
    
    def visit_NameConstant(self, cons):
        c = {None : NONE, False : BOOL, True : BOOL}
        return c[cons.value]

    def visit_ListComp(self, value):
        gen = value.generators[0]
        name = gen.target.id
        val = self.getseq(gen)
        assert val != []
        v = Visitor(self)
        for i in val:
            v.bind_weak(name, i.TypeSet())
        '''
        vall = v.visit(value.elt)
        res = SEQ.fromset(vall)
        assert not isinstance(res, TypeSet)
        
        return res
        '''
        return ANY
 
    def visit_Lambda(self, lmb):
        returns = self.visit(lmb.body) 
        return self.create_func(lmb.args, returns, 'lambda')

    def visit_Expr(self, expr):
        self.visit(expr.value)
    
    def visit_arguments(self, args):
        return Arguments(args)
        
    def getseq(self, expr):
        return TypeSet({v for v in self.visit(expr.iter) if augisinstance(v, SEQ)})
    
    def create_func(self, args, returns, t):
        args.defaults = [self.visit(i) for i in args.defaults]
        args.kw_defaults = [(self.visit(i) if i != None else i) for i in args.kw_defaults ]
        return Function(args, lambda *x : returns, t)


if __name__=='__main__':
    import analyze
    analyze.main()
    