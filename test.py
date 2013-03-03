import networkx as nx
def foo():
    global x
    x=5
    def bar():
        nonlocal z
        z=9
        f=8
        pass
    global kill
    def kill():
        pass
    z=7

y=6
foo()
print(x)