class A:
    def __init__(self):
        self.z = 6
A.foo = lambda s : 1
x=A()
x.foo = lambda k : 2
p = x.foo(2)