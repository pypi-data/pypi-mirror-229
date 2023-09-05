
from flowhigh.model.Direction import Direction
from flowhigh.model.Attr import Attr


class StructRef(Attr):
    refpath: str = None

    def __init__(self):
        super().__init__()



from flowhigh.model.TreeNode import TreeNode

class StructRefBuilder (object):
    construction: StructRef

    
    def __init__(self) -> None:
        super().__init__()
        self.construction = StructRef()
    
    def with_refsch(self, refsch: str):
        child = refsch
        self.construction.refsch = child
    
    def with_fullref(self, fullref: str):
        child = fullref
        self.construction.fullref = child
    
    def with_refvar(self, refvar: str):
        child = refvar
        self.construction.refvar = child
    
    def with_refdb(self, refdb: str):
        child = refdb
        self.construction.refdb = child
    
    def with_pos(self, pos: str):
        child = pos
        self.construction.pos = child
    
    def with_refds(self, refds: str):
        child = refds
        self.construction.refds = child
    
    def with_refpath(self, refpath: str):
        child = refpath
        self.construction.refpath = child
    
    def with_alias(self, alias: str):
        child = alias
        self.construction.alias = child
    
    def with_refatt(self, refatt: str):
        child = refatt
        self.construction.refatt = child
    
    def with_refoutidx(self, refoutidx: str):
        child = refoutidx
        self.construction.refoutidx = child
    
    def with_direction(self, direction: Direction):
        child = direction
        self.construction.direction = child

    def build(self):
        return self.construction
