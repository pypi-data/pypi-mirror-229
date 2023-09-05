
from flowhigh.model.Statement import Statement
from flowhigh.model.TypeCast import TypeCast


class DeleteStatement(Statement, TypeCast):
    type_: str = None
    

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class DeleteStatementBuilder (object):
    construction: DeleteStatement
    

    def __init__(self) -> None:
        super().__init__()
        self.construction = DeleteStatement()
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_antiPatterns(self, antiPatterns: list):
        child = antiPatterns
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), antiPatterns)):
            self.construction.add_child(node)
        self.construction.antiPatterns = child
    
    def with_rawInput(self, rawInput: str):
        child = rawInput
        self.construction.rawInput = child
    
    def with_type(self, type_: str):
        child = type_
        self.construction.type_ = child
    
    def with_ds(self, ds: list):
        child = ds
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), ds)):
            self.construction.add_child(node)
        self.construction.ds = child

    def build(self):
        return self.construction
