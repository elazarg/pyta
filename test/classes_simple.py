a=1
a=1

class A:
    q=4
    def kill(self):
        return 6

A.p=5
six = A.kill(A())
six1 = A().kill()
pp=A.p
qq=A.q
x=A()

def foo():
    return 1
y=foo(x)

class B:
    def __init__(self, e):
        pass
    
    def bar(self):
        pass

z=B(1)