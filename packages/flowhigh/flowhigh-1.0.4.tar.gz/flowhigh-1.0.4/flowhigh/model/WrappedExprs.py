


class WrappedExprs(object):
    exprs: list = []

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class WrappedExprsBuilder (object):
    construction: WrappedExprs

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = WrappedExprs()
    
    def with_exprs(self, exprs: list):
        child = exprs
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), exprs)):
            self.construction.add_child(node)
        self.construction.exprs = child

    def build(self):
        return self.construction
