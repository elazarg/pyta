import ast
t=2

class Q:
    def get_x(self):
        return 5
    x=property(get_x)
print(Q().x)
'''
def bla(t):
    nonlocal t
    t=5
bla()
print(t)
class Q:
    g=3
x=5
y=x
z='hello'

def foo():
    pass
def bar():
    pass
foo(bar())
def bla(b):
    x=5 
    g=b
z=5
x=5
y=bla(x)
def foo(y):
    global x
    x=5
    z=y
x=3
w=foo(3)
class A:
    def bar(self):
        pass
    
x=(5,False)
z=foo(1,2)
x=3
y1,y2 =(1,2)
for i in x:
    pass

'''
'''
x,y=3,4
class A:
    #global xx
    xx=5
    y=xx
with A as q, B as r:
    pass
'''