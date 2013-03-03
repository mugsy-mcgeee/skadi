def build_with(dts):
    tree = Tree(None)

    for dt in dts:
        lineage = [dt]
        gen     = (a for a in dts if a.name == dt.baseclass)
        if dt.baseclass:
            ancestor = next(gen, None)
            while ancestor:
                lineage.insert(0, ancestor)
                gen      = (a for a in dts if a.name == ancestor.baseclass)
                ancestor = next(gen, None)
        [tree.place(dt) for dt in lineage]

    return tree

class NodeFound(Exception):
    def __init__(self, match, depth):
        self.match = match
        self.depth = depth

class Node(object):
    def __init__(self, dt, parent=None):
        self.dt       = dt
        self.parent   = parent
        self.children = []

    def select(self, callable, found, depth=0):
        for child in self.children:
            child.select(callable, found, depth=depth+1)
        if callable(self, depth):
            found.append(self)

    def lineage(self, found=None):
        if self.parent:
            found = self.parent.lineage(found=[])

        if self.dt:
            found.append(self)

        return found

    def find(self, callable, depth=0):
        if callable(self):
            raise NodeFound(self, depth)
        for child in self.children:
            child.find(callable, depth+1)

    def traverse(self, callable, depth=0):
        for child in self.children:
            child.traverse(callable, depth=depth+1)
        callable(self, depth)

class Compares:
    def __init__(self, dt_name):
        self.dt_name = dt_name

    def __call__(self, other):
        return self.dt_name == other.dt.name

class ComparesBaseclass:
    def __init__(self, dt_baseclass):
        self.dt_baseclass = dt_baseclass

    def __call__(self, other):
        return self.dt_baseclass == other.dt.name

class Tree(object):
    def __init__(self, base_entity):
        self.root = Node(base_entity)

    def place(self, dt):
        if self.contains(dt.name):
            return

        parent = self.find(ComparesBaseclass(dt.baseclass))
        if parent:
            siblings = parent.children
            gen      = (s for s in siblings if s.dt.name == dt.name)

            if next(gen, None):
                return

            node = Node(dt, parent=parent)
            siblings.append(node)
        else:
            node = Node(dt, parent=self.root)
            self.root.children.append(node)

        return node

    def contains(self, dt_name):
        return self.find(Compares(dt_name))

    def traverse(self, callable):
        for child in self.root.children:
            child.traverse(callable)

    def select(self, callback):
        found = []
        for child in self.root.children:
            child.select(callback, found=found)
        return found

    def find(self, callable):
        found = None
        try:
            for child in self.root.children:
                child.find(callable) 
        except NodeFound as nf:
            found = nf.match
        return found