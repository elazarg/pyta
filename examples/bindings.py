def foo(x):
    global z
    def bar():
        global d
        nonlocal y
        y=2
        b=3
        d=4
        class B:
            nonlocal d
            global f
            d=6
            u=3
            f=7
    nonlocal foo
    z=5
    y=4
    d=2
class A:
    global b
    a=3
    b=2
t=4