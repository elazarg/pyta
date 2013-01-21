class object:
    def __eq__(self, other):
        return False
    def __ge__(self, other):
        return False
    def __le__(self, other):
        return False
    def __lt__(self, other):
        return False
    def __ne__(self, other):
        return False
    def __gt__(self, other):
        return False
    
    def __class__(self):
        return None
    def __delattr__(self):
        return None
    def __setattr__(self):
        return None
    
    def __sizeof__(self):
        return 0
    
    def __doc__(self):
        return {"":""}
    
    def __repr__(self):
        return ""
    def __str__(self):
        return ""
    def __hash__(self):
        return ""
    
    def __init__(self):
        return self
    def __new__(self):
        return self
    