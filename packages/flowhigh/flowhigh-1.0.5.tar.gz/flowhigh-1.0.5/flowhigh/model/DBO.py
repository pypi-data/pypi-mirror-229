
from flowhigh.model.DBOType import DBOType
from flowhigh.model.TreeNode import TreeNode


class DBO(TreeNode):
    dbo: list = []
    name: str = None
    dtype: str = None
    index: str = None
    constraint: str = None
    oid: str = None
    type_: DBOType = None
    

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class DBOBuilder (object):
    construction: DBO
    

    def __init__(self) -> None:
        super().__init__()
        self.construction = DBO()
    
    def with_dbo(self, dbo: list):
        child = dbo
        for node in list(filter(lambda el: TreeNode in el.__class__.mro(), dbo)):
            self.construction.add_child(node)
        self.construction.dbo = child
    
    def with_name(self, name: str):
        child = name
        self.construction.name = child
    
    def with_index(self, index: str):
        child = index
        self.construction.index = child
    
    def with_dtype(self, dtype: str):
        child = dtype
        self.construction.dtype = child
    
    def with_constraint(self, constraint: str):
        child = constraint
        self.construction.constraint = child
    
    def with_oid(self, oid: str):
        child = oid
        self.construction.oid = child
    
    def with_type(self, type_: DBOType):
        child = type_
        self.construction.type_ = child

    def build(self):
        return self.construction
