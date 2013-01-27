def a():
    pass

a()
def b():
    return 0

anint = b()
'''

def c(x):
    return
c(1)

def d(x, y):
    pass  

d(1,2)

def e(x=5):
    pass

e()
e(1)

def f(x, y=5):
    pass

f(1)
f(1,2)

def g(*sequence):
    pass

g()
g(1)
g(1,2)

def h(x, y=5, *sequence):
    pass

h(1)
h(1,2)
h(1,2,3)
h(1,2,3,4)
h(1,2,3,4,5)

def i(x, y=5, *sequence, z=3):
    pass

i(1)
i(1,2)
i(1,2,3)
i(1,2,3,4)
i(1,2,3,4,5)

i(1, z=6)
i(1,2, z=6)
i(1,2,3, z=6)
i(1,2,3,4, z=6)
i(1,2,3,4,5, z=6)
def j(x, y=5, *sequence, z=3, **dic):
    pass

j(1)
j(1,2)
j(1,2,3)
j(1,2,3,4)
j(1,2,3,4,5)

j(1, z=6)
j(1,2, z=6)
j(1,2,3, z=6)
j(1,2,3,4, z=6)
j(1,2,3,4,5, z=6)

j(1, z=6, q=5)
j(1,2, z=6, q=5)
j(1,2,3, z=6, q=5)
j(1,2,3,4, z=6, q=5)
j(1,2,3,4,5, z=6, q=5)
'''