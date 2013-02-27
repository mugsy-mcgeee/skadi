from random import choice
from skadi.cli.model.server_entity import Property

class EntityTreeLocated(Exception):
    def __init__(self, entity_tree):
        self.entity_tree = entity_tree

class EntityTree(object):
    def __init__(self, entity, parent=None):
        self.entity   = entity
        self.parent   = parent
        self.children = []

    def aggregate_properties(self, properties=[]):
        try:
            working = self.entity.properties + properties
        except AttributeError:
            working = properties

        if self.parent:
            return self.parent.aggregate_properties(properties=working)
        return working

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

            aggregate = map(lambda p: (p, p.name, p.origin.name), child.aggregate_properties())
            relevant  = [(p, pn, pon) for p, pn, pon in aggregate if p.name != 'baseclass']

            print "Properties of %s:" % entity.name
            for p, pn, pon in relevant:
                flags   = bin(p.flags if p.flags else 0)[2:].zfill(20)
                exclude = True if p.flags & Property.FLAGS['exclude'] else False

                if exclude:
                    msg = "  EXCLUDE INHERITED ATTR: %s" % (p.name.ljust(32))
                else:
                    if p.bits:
                      elab = ' %i-bit' % p.bits
                    elif pn != 'baseclass' and p.data_type:
                      elab = ' %s' % p.data_type
                    else:
                      elab = ''
                    msg = "  %s p=%s; t=%i; f=%s %s (%s)" % (p.name.ljust(32), str(p.priority).rjust(3, ' '), p.type, flags, elab, pon)

                print msg
            print
