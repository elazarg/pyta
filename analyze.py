#!/sbin/python3

'''
TODO:

* type variables (lazy/memoizable?)
* augmented assignment
* single-valued-ints
* better ListComp (more specific)
* Exceptions

* better type-error warnings
* strict support for some sublanguage
* milestone - sit with Yuri/Eran

* attributes
* metaclasses

* basic control flow
* full CFG

* porting to c++ ?
* porting to datalog ?!
* some DSL
* basic framework
'''
import visitor, ast

def readfile(filename, module = None):
    return ast.parse(open(filename).read())

def pretest():  
    basedir = 'test/'
    files = ['primitives.py',
             'assign_simple.py', 'assign_multi.py',
             'functions_and_calls.py',
              'classes_simple.py'
              ]                 
    for file in files:
        print('test :', file)
        res = visitor.Visitor()
        res.visit(readfile(basedir + file))
        print('test :', file, 'done')
    print('pretest done')
    return res
 
def prelude():  
    g = visitor.Visitor()
    basedir = 'database/'
    files = ['object.py', 'int.py', 'float.py', 'complex.py',
             #'list.py',
              'functions.py']                 
    for file in files:
        g.visit(readfile(basedir + file))
    g.print()
    return g

def main():
    r = pretest()
    r.print()
    return
    g = prelude()
    v = visitor.Visitor(g)
    r = readfile('test/parsed.py')
    v.visit(r)
    v.print()
            

if __name__=='__main__':
    main()