from skadi.cli.model.tree import Tree, Compares
from skadi.cli.model.sendprop import Sendprop

def amass_exclusions(tree, dt):
    ss         = dt.sendprops
    exclusions = [(s.name, s.dt_name) for s in ss if s.flagged_EXCLUDE()]
    inclusions = [s for s in ss if not s.flagged_EXCLUDE()]

    for s in inclusions:
        if s.flagged_COLLAPSIBLE():
            _dt        = tree.find(Compares(s.dt_name)).dt
            exclusions = exclusions + amass_exclusions(tree, _dt)

    return list(set(exclusions))

def amass_sendprops(tree, dt, exclusions):
    ss         = dt.sendprops
    inclusions = [s for s in ss if not s.flagged_EXCLUDE()]

    heap = []
    for s in inclusions:
        if s.flagged_COLLAPSIBLE():
            _dt  = tree.find(Compares(s.dt_name)).dt
            heap = amass_sendprops(tree, _dt, exclusions) + heap
        else:
            heap.append(s)

    return [s for s in heap if (s.name, s.origin.name) not in exclusions]

def order_sendprops(heap):
    heap  = sorted(heap, key=lambda s: s.priority)

    pre   = [s for s in heap if s.priority  < 128]
    bump  = [s for s in heap if s.flagged_CHANGESOFTEN() and s not in pre]
    post  = [s for s in heap if s.priority == 128 and not s.flagged_CHANGESOFTEN()]

    return pre + bump + post

class Encoder(object):
    def __init__(self, sendprops, exclusions):
        self.sendprops  = sendprops
        self.exclusions = exclusions