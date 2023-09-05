
from flowhigh.model.CoordinateBlock import CoordinateBlock


class Statement(CoordinateBlock):
    pos: str = None
    antiPatterns: list = []
    rawInput: str = None
    ds: list = []
    

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class StatementBuilder (object):
    construction: Statement
    

    def __init__(self) -> None:
        super().__init__()
        self.construction = Statement()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_rawInput(self, rawInput: str):
        child = rawInput
        self.construction.rawInput = child
    
    def with_antiPatterns(self, antiPatterns: list):
        child = antiPatterns
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), antiPatterns)):
            self.construction.add_child(node)
        self.construction.antiPatterns = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child

    def build(self):
        return self.construction
