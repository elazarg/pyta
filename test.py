import networkx as nx
x=7
def foo():
    y=5
    def bar():
        nonlocal x
        print(x)
    print(y)
    bar()

foo()
print(x)