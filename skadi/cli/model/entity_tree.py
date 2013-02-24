from random import choice

class EntityTreeLocated(Exception):
    def __init__(self, entity_tree):
        self.entity_tree = entity_tree

class EntityTree(object):
    def __init__(self, entity, parent=None):
        self.entity   = entity
        self.parent   = parent
        self.children = []

    def debug_by_traversal(self, depth=0):
        if self.entity is None:
            for child in self.children:
                child.debug_by_traversal(depth=0)
        else:
            print "%s+ %s" % ('  ' * depth, self.entity.name)
            for child in self.children:
                child.debug_by_traversal(depth=(depth+1))

    def locate_parent(self, entity, depth=0):
        if self.entity is None and entity.baseclass is None:
            raise EntityTreeLocated(self)
        elif self.entity and self.entity.name == entity.baseclass:
            raise EntityTreeLocated(self)
        for child in self.children:
            child.locate_parent(entity, depth=(depth+1))

class EntityClassHierarchy(object):
    def __init__(self, entities):
        self.entities = entities
        self.root     = EntityTree(None)
        for entity in self.entities:
            gen     = (a for a in self.entities if a.name == entity.baseclass)
            lineage = [entity]
            if entity.baseclass is not None:
                anc = next(gen, None)
                while anc:
                    lineage.insert(0, anc)
                    gen = (a for a in self.entities if a.name == anc.baseclass)
                    anc = next(gen, None)
            [self.place(entity) for entity in lineage]

    def place(self, entity):
        parent_tree = None
        try:
            self.root.locate_parent(entity)
        except EntityTreeLocated as state:
            parent_tree = state.entity_tree

        if parent_tree:
            siblings  = map(lambda c: c.entity, parent_tree.children)
            generator = (s for s in siblings if s.name == entity.name)
            if next(generator, None):
                return

            child = EntityTree(entity, parent=parent_tree)
            parent_tree.children.append(child)
