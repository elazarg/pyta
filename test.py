
def foo():
    for j in (1,2,3):
        yield j
def bar():
    yield from (1, 2, 3)
    
for j in foo():
    z=j
    
for k in bar():
    t=k


tt = [i for i in (1,2) if i]