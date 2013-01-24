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
import visitor, ast

def readfile(filename, module = None):
    return ast.parse(open(filename).read())

def main():
    v = visitor.Visitor()
    #m.run(readfile('database/functions.py'))
    #m.run(readfile('database/Object.py'))
    r = readfile('test/parsed.py')
    v.visit(r)
    
    for i in v.sym.vars:
        for k,v in i.items():
            print('{0} : {1}'.format(k,v))
            

if __name__=='__main__':
    main()