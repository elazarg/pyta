
class A:
    def invariant(m):
        def wrapped(self, *args):
            res = m(self, *args)
            self.to_invariant()
            return res
        return wrapped
    
    @invariant
    def foo(self, i):
        print(i)
        
    def to_invariant(self):
        print(2)
        
x=A()
x.foo(3)