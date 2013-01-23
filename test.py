'''
Created on Jan 22, 2013

@author: elazar
'''
from ast import *
a='''class A:
    x=5
    def foo(self):
        pass
    '''

print(dump(parse('A.foo()')))
'''
Module(body=
[ClassDef(name='A', bases=[], keywords=[], starargs=None, kwargs=None,
     body=[Assign(targets=[Name(id='x', ctx=Store())], value=Num(n=5)), Pass()], decorator_list=[])])

Module(
body=[ClassDef(name='A', bases=[], keywords=[], starargs=None, kwargs=None,
     body=[Assign(targets=[Name(id='x', ctx=Store())], value=Num(n=5)),
      FunctionDef(name='foo', args=arguments(args=[arg(arg='self', annotation=None)], vararg=None, varargannotation=None, kwonlyargs=[], kwarg=None, kwargannotation=None, defaults=[], kw_defaults=[]), body=[Pass()], decorator_list=[], returns=None)], decorator_list=[])])

'''