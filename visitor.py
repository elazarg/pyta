#!/sbin/python3
import ast 
from types import TypeSet, Class, Specific, ANY, st, join, joinall
from types import BOOL, INT, FLOAT, NONE, COMPLEX, TRUE, FALSE
from types import BYTES, STR, TUPLE, LIST, SEQ, DICT
from definitions import Function, Arguments
from symtable import SymTable

def augisinstance(s, t): 
    return s==ANY or isinstance(s,t)

def visit_result(method):
    def wrapped(self, args):
        #ast.dump(args)
        res = method(self, args)
        assert issubclass(type(res), ast.AST)
        return self.visit(res)
    return wrapped

def analyze_file(filename, path=()):
    import pyclbr
    d = pyclbr.readmodule_ex(filename, path)
    stub = lambda k, v : Class(v.name) if isinstance(v, pyclbr.Class) else Class('Function').instance
    sym = SymTable({k:stub(k, v) for k, v in d.items()})
     
    x = ast.parse(open(path[0] + filename + '.py').read())
    
    from ast_transform import Transformer
    #print(codegen.to_source(x))
    Transformer().visit(x)
    
    import codegen
    print(codegen.to_source(x))
    
    res = Visitor()
    #res.sym = sym
    res.visit(x)
    return res


class Visitor(ast.NodeVisitor):
    
    def generic_visit(self, node):
        for n in ast.iter_child_nodes(node):
            self.visit(n)
    
    def __init__(self, parent = None):
        if parent != None:
            self.sym = SymTable(parent.sym)
        else:
            self.sym = SymTable()
        self.parent = parent
        
        if parent == None:
            d = {'int' : INT, 'bool' : BOOL, 'float' : FLOAT, 'complex' : COMPLEX}
            for k, v in d.items(): 
                self.bind_weak(k, v)
    
    def lookup(self, name):
        res = self.sym.get_var(name)
        '''
        if self.parent and res == None:
            return self.parent.lookup(name)
        '''
        return res
    
    def bind_weak(self, var_id, anInstance):        
        self.sym.bind(var_id, anInstance)
    
    def print(self):
        self.sym.print()
    
    def visit_Assign(self, ass):
        val = self.visit(ass.value)
        for target in ass.targets:
            if isinstance(target, ast.Name):
                self.bind_weak(target.id, val) 
            elif isinstance(target, ast.Attribute):
                self.visit(target.value).bind(target.attr, val)
            elif isinstance(target, ast.Tuple):
                size = len(target.elts)
                target_matrix = [v.split_to(size) for v in val if augisinstance(v, SEQ) and v.can_split_to(size)]
                assert target_matrix != []
                target_tuple = [val.union_all([v[i] for v in target_matrix]) for i in range(size)]
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
        return self.visit(value).lookup(name)
    
    def visit_Attribute(self, attr):
        return self.get_attr_types(attr.value, attr.attr)

    def visit_FunctionDef(self, func):
        #TODO : add type variables
        #TODO : support self-references through symtable
        v = Visitor(self)
        returns = v.run(func)
        if not returns:
            returns = NONE
        res = self.create_func(func.args, returns, 'func')
        self.bind_weak(func.name, st(res))
    
    def visit_ClassDef(self, cls):
        #assume for now that methods only calls previous ones
        v = Visitor(self)
        v.run(cls)
        c = Class(cls.name, v.sym)
        
        builtins = {'float', 'complex', 'int'}
        if cls.name in builtins:
            self.lookup(cls.name).readjust(cls.name)
        self.bind_weak(cls.name, c)
            
    def visit_Call(self, value):
        value.args = [self.visit(i) for i in value.args]
        for keyword in value.keywords:
            keyword.value = self.visit(keyword.value)
        func = value.func
        if isinstance(func, ast.Name):
            res = self.visit(func).call(value)
        elif isinstance(func, ast.Attribute):
            res = self.get_attr_types(func.value, func.attr).call(value)
            #if None in res:             print('recursive class definition found')
        return res
            
    def visit_IfExp(self, ifexp):
        return join(self.visit(ifexp.body), self.visit(ifexp.orelse))
    
    def visit_Subscript(self, sub):
        assert False

    def visit_BinOp(self, binop):
        assert False
    
    def visit_If(self, stat):
        return self.visit_all_childs(stat)
    
    def visit_While(self, stat):
        def go_round(node):
            #TODO : better comparison
            old_sym = repr(self.sym)
            ret = self.visit_all_childs(node)
            new_sym = repr(self.sym)
            return ret, old_sym == new_sym
        while True:
            ret, done = go_round(stat)
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
        return NONE if ret.value == None else self.visit(ret.value)

    def run(self, node):
        return joinall(self.visit(n) for n in node.body)

    def visit_Module(self, node):
        return self.run(node)
      
    def visit_Num(self, value):
        types = { int : 'int', float : 'float', complex : 'complex' }
        name = types.get(type(value.n))
        if name == None:
            print('unknown Num:', ast.dump(value))
            return None
        return Specific.factory(self.lookup(name), value.n)
    
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
        return self.lookup(value.id)
    
    def visit_NameConstant(self, cons):
        c = {None : NONE, False : FALSE, True : TRUE}
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
    