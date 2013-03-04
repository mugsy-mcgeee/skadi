from skadi.cli.model.tree import Tree, Compares
from skadi.cli.model.sendprop import Sendprop

def amass_exclusions(tree, dt):
    ss         = dt.sendprops
    exclusions = [(s.name, s.dt_name) for s in ss if s.is_exclusion()]
    inclusions = [s for s in ss if not s.is_exclusion()]

    for s in inclusions:
        if s.is_ancestral():
            _dt        = tree.find(Compares(s.dt_name)).dt
            exclusions = amass_exclusions(tree, _dt) + exclusions

    return exclusions

def amass_sendprops(tree, dt, exclusions):
    ss         = dt.sendprops
    inclusions = [s for s in dt.sendprops if (s.name, s.origin.name) not in exclusions]

    heap = []
    for s in inclusions:
        if s.is_ancestral():
            _dt  = tree.find(Compares(s.dt_name)).dt
            heap = amass_sendprops(tree, _dt, exclusions) + heap
        elif not s.is_serveronly():
            heap.append(s)

    return [s for s in heap if (s.name, s.origin.name) not in exclusions]

def order_sendprops(heap):
    heap  = sorted(heap, key=lambda s: s.priority)

    pre   = [s for s in heap if s.priority  < 128]
    bump  = [s for s in heap if s.is_bumped()]
    post  = [s for s in heap if s.priority == 128 and not s.is_bumped()]

    return pre + bump + post

class Encoder(object):
    def __init__(self, sendprops, exclusions):
        self.sendprops  = sendprops
        self.exclusions = exclusions