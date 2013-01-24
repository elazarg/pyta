#!/sbin/python3

'''
TODO:

* add binop support
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

  
def prelude():  
    g = visitor.Visitor()
    g.visit(readfile('database/object.py'))
    g.visit(readfile('database/int.py'))
    g.visit(readfile('database/float.py'))    
    g.visit(readfile('database/list.py'))    
    g.visit(readfile('database/functions.py'))
    g.print()
    return g

def main():
    #g = prelude()
    v = visitor.Visitor()
    r = readfile('test/parsed.py')
    v.visit(r)
    v.print()
            

if __name__=='__main__':
    main()