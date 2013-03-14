#!/sbin/python3

'''
TODO:

* type variables (lazy/memoizable?)
* single-valued-ints
* better ListComp (more specific)
* Exceptions

* better type-error warnings
* strict support for some sublanguage
* milestone - sit with Yuri/Eran

* metaclasses

* basic control flow
* full CFG

* porting to c++ ?
* porting to datalog ?!
* some DSL
* basic framework
'''
import visitor, ast, codegen
from visitor import analyze_file

def pretest():  
    basedir = 'test/'
    files = ['primitives',
             'assign_simple',
             # 'assign_multi',
             'functions_and_calls',
             'classes_simple'
              ]                 
    for file in files:
        print('test :', file)
        analyze_file(file, [basedir]).print()
        print('test :', file, 'done')
    print('pretest done')
 
def prelude():  
    g = visitor.Visitor()
    basedir = 'database/'
    files = ['object', 'int', 'float', 'complex',
             #'list',
              'functions']                 
    for file in files:
        g.translate(analyze_file(basedir + file))
    g.print()
    return g

def main():
    pretest()
    return
    g = prelude()
    v = visitor.Visitor(g)
    r = analyze_file('test/parsed.py')
    v.translate(r)
    v.print()
            

if __name__=='__main__':
    main()