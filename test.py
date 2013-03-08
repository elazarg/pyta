y='fgd'
foo = lambda y : lambda x : lambda z : x
#def foo(x): return x
seq = (1,2)
seq = 'jk'
for i in seq:
    x=foo(i)(i)
    
class A:
    def __exit__(self):
        pass
    
    def __enter__(self):
        pass
z=A()
z=1
with z as f:
    pass
