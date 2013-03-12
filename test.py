
def foo():
    for j in (1,2,3):
        yield j
def bar():
    yield from (1, 2, 3)
    
for i in foo():
    z=i
    
for k in bar():
    t=k


