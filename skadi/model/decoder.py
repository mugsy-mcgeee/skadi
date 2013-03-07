from skadi.model.tree import Tree, Compares
from skadi.model.sendprop import Sendprop, Type

def build_with(registry):
    return Decoder(registry)

class Decoder(object):
    def __init__(self, registry):
        self.registry = registry

    def flatten(self, dt):
        pass

    # def exclusions(self, dt):
    #     ss   = dt.sendprops
    #     excl = [(dt.name, s.dt_name, s.name) for s in ss if s.fExclude()]
    #     incl = [s for s in ss if not s.fExclude()]

    #     for s in incl:
    #         if s.type == Type.DATATABLE[1]:
    #             _dt  = tree.find(Compares(s.dt_name)).dt
    #             excl = exclusions(tree, _dt) + excl

    #     return excl

    # def amass_sendprops(self, dts):
    #     return sum(map(lambda dt: dt.sendprops, dts), [])

    # def amass_flatprops(self, dt, excl):
    #     heap = []
    #     for s in dt.sendprops:
    #         if not s.fExclude():
    #             if s.fCollapsible():
    #                 _dt  = tree.find(Compares(s.dt_name)).dt
    #                 heap = amass_sendprops(tree, _dt, excl) + heap
    #             else:
    #                 heap.append(s)

    #     trimmed_excl = map(lambda e: e[1:], excl)
    #     return [s for s in heap if (s.origin.name, s.name) not in trimmed_excl]

    # def order_sendprops(self):
    #     heap  = sorted(heap, key=lambda s: s.priority)

    #     pre   = [s for s in heap if s.priority  < 128]
    #     bump  = [s for s in heap if s.fChangesOften() and s not in pre]
    #     post  = [s for s in heap if s.priority == 128 and not s.fChangesOften()]

    #     return pre + bump + post
