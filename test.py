def fib(n):
    if n == 0:
        return 0
    if n == 1:
        return 1 
    return fib(n-1) + fib(n-2)

q=fib(40+4)

def fib_iter(n):
    a,b = 0,1
    for _ in range(n):
        a, b = b, a+b
    return b


def foo(etc):
    def bar():
        return etc
    return bar

x=foo(fib)

def t(x):
    return x

y=t(1)

a=1
b=2
a,b=b,a
