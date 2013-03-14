def a():
    return 'a1'
a1 = a()

def b():
    return 'b1'
b1 = b()


def c(x):
    return x
c1 = c(1)

def d(x, y):
    return (x, y)  

d1 = d(1,2)

def e(x=5):
    return x

e1 = e()
e2 = e('g')

def f(x, y=5):
    return y

f1 = f(1)
f2 = f(1,'g')

def g(*sequence):
    return sequence

g1 = g()
g2 = g(1)
g3 = g(1,2)

def h(x, y=5, *sequence):
    return y

h1 = h(1)
h2 = h(1,2)
h3 = h(1,2,3)
h4 = h(1,2,3,4)
h5 = h(1,2,3,4,5)
def i(x, y=5, *sequence, z=3):
    return z

i1 = i(1)
i2 = i(1,2)
i3 = i(1,2,3)
i4 = i(1,2,3,4)
i5 = i(1,2,3,4,5)

i6 = i(1, z=6)
i7 = i(1,2, z=6)
i8 = i(1,2,3, z=6)
i9 = i(1,2,3,4, z=6)
i10 = i(1,2,3,4,5, z=6)

def j(x, y=5, *sequence, z=3, **dic):
    '**dic does not really work currently'
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
