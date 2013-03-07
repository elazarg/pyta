#!/sbin/python3
import ast 
from targettypes import TypeSet, Class, Specific, ANY, st, meet, meetall
from targettypes import BOOL, INT, FLOAT, NONE, COMPLEX, TRUE, FALSE, TYPE
from targettypes import BYTES, TUPLE, LIST, SEQ, DICT
from definitions import Function, Arguments
from symtable import SymTable
from bindfind import find_bindings
from ast import NodeVisitor

def augisinstance(s, t): 
    return s==ANY or isinstance(s,t)
    
class Visitor(NodeVisitor):
   
    def generic_visit(self, node):
        for n in ast.iter_child_nodes(node):
            self.translate(n)
    
    def __init__(self, parent):
        self.sym = SymTable()
        self.parent = parent
        self.globals = parent.globals
    
    def make_namespaces(self, node):
        self.bindings = find_bindings(node)
        return meetall(self.translate(n) for n in node.body)

    def visit_Module(self, node):
        assert False
   
    def find_namespace(self, name):
        if name in self.bindings.globals:
            #there is global declaration
            return self.globals
        if name in self.bindings.nonlocals:
            #there is nonlocal declaration
            res = self.parent.find_namespace(name)
            if res == self.globals:
                #error - nonlocals cannot be globals
                return TypeSet({})
        if name in self.bindings.locals:
            #there is binding in local body, and no special declaration
            return self.sym
        return self.parent.find_namespace(name)    
       
    def bind_lookups(self, name):
        return self.find_namespace(name).get_var(name)
     
    def bind_weak(self, name, anInstance):
        return self.find_namespace(name).bind(name, anInstance)
    
    def print(self):
        self.sym.print()
    
    def visit_Assign(self, node):
        val = self.translate(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.bind_weak(target.id, val) 
            elif isinstance(target, ast.Attribute):
                self.translate(target.value).bind(target.attr, val)
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
            res = self.translate(n)
            if isinstance(n, ast.stmt) and res != None:
                returns.update(res)
        return returns
    
    def get_attr_types(self, value, name):
        return self.translate(value).bind_lookups(name)
    
    def visit_Attribute(self, attr):
        return self.get_attr_types(attr.value, attr.attr)

    def visit_FunctionDef(self, func):
        #TODO : add type variables
        v = Visitor(self)
        returns = v.make_namespaces(func)
        if not returns:
            returns = NONE
        res = self.create_func(func.args, returns, func.name)
        if func.name in self.presym:
            'Yack. and probably completely wrong: memberwise-assignment'
            self.bind_lookups(func.name).__dict__ = res.__dict__
        else:        
            self.bind_weak(func.name, st(res))
    
    def visit_ClassDef(self, cls):
        #assume for now that methods only calls previous ones
        #self.bind_weak(cls.name, Class('@temp'))
        v = Visitor(self, name=cls.name)
        v.make_namespaces(cls)
        c = Class(cls.name, v.sym)
        builtins = {'float', 'complex', 'int'}
        if cls.name in self.presym or cls.name in builtins:
            'Yack. and probably completely wrong: memberwise-assignment'
            self.bind_lookups(cls.name).__dict__ = c.__dict__
        else:
            self.bind_weak(cls.name, c)
            
    def visit_Call(self, node):
        node.args = [self.translate(i) for i in node.args]
        for keyword in node.keywords:
            keyword.value = self.translate(keyword.value)
        func = node.func
        if isinstance(func, ast.Name):
            res = self.translate(func).call(node)
        elif isinstance(func, ast.Attribute):
            res = self.get_attr_types(func.value, func.attr).call(node)
            #if None in res:             print('recursive class definition found')
        return res
            
    def visit_IfExp(self, ifexp):
        return meet(self.translate(ifexp.body), self.translate(ifexp.orelse))
    
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
        return NONE if ret.value == None else self.translate(ret.value)

    def visit_Num(self, value):
        types = { int : 'int', float : 'float', complex : 'complex' }
        name = types.get(type(value.n))
        if name == None:
            print('unknown Num:', ast.dump(value))
            return None
        return Specific.factory(self.bind_lookups(name), value.n)
    
    def visit_Str(self, value):
        return STR
    
    def visit_Bytes(self, value):
        return BYTES

    def visit_Dict(self, value):
        keys=[self.translate(i) for i in value.keys]
        values=[self.translate(i) for i in value.values]
        return DICT(keys,values)

    def visit_Tuple(self, value):
        return TUPLE([self.translate(i) for i in value.elts])
        
    def visit_List(self, value):
        return LIST([self.translate(i) for i in value.elts])

    def visit_Name(self, value):
        return self.bind_lookups(value.id)
    
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
        vall = v.translate(value.elt)
        res = SEQ.fromset(vall)
        assert not isinstance(res, TypeSet)
        
        return res
        '''
        return ANY
 
    def visit_Lambda(self, lmb):
        returns = self.translate(lmb.body) 
        return self.create_func(lmb.args, returns, '<lambda>')

    def visit_Expr(self, expr):
        self.translate(expr.value)
    
    def visit_arguments(self, args):
        return Arguments(args)
        
    def getseq(self, expr):
        return TypeSet({v for v in self.translate(expr.iter) if augisinstance(v, SEQ)})
    
    def create_func(self, args, returns, name):
        args.defaults = [self.translate(i) for i in args.defaults]
        args.kw_defaults = [(self.translate(i) if i != None else i) for i in args.kw_defaults ]
        return Function(args, lambda *x : returns, name)


class ModuleVisitor(Visitor):
    def __init__(self):
        self.globals = self.sym = SymTable()
        d = {'int' : INT, 'bool' : BOOL, 'float' : FLOAT, 'complex' : COMPLEX, 'type' : TYPE}
        for k, v in d.items(): 
            self.bind_weak(k, v)
    
    def find_namespace(self, name):
        return self.sym    

    def visit_Module(self, node):
        return self.make_namespaces(node)
    
def analyze_file(filename, path=()):
    '''
    import pyclbr
    d = pyclbr.readmodule_ex(filename, path)
    stub = lambda k, v : Class('@temp') if isinstance(v, pyclbr.Class) else Function.get_generic()
    sym = {k:stub(k, v) for k, v in d.items()}
    '''
    x = ast.parse(open(path[0] + filename + '.py').read())
    from ast_transform import Transformer
    #print(codegen.to_source(x))
    Transformer().translate(x)
    
    import codegen
    print(codegen.to_source(x))
    
    res = ModuleVisitor()
    #res.sym = sym
    res.translate(x)
    return res

     
if __name__=='__main__':
    import analyze
    analyze.main()
    