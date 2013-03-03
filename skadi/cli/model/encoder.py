from skadi.cli.model.tree import Tree, Compares
from skadi.cli.model.sendprop import Sendprop

def amass_sendprops(tree, dt, heap=None):
    if heap is None:
        heap = []

    excl = [(e.name, e.dt_name) for e in dt.sendprops if e.is_excluded()]
    incl = [s for s in dt.sendprops if not e.is_excluded()]

    baseclass = next((e for e in dt.sendprops if e.name == 'baseclass'), None)
    if baseclass:
        baseclass_dt = tree.find(Compares(baseclass.dt_name)).dt
        heap         = amass_sendprops(tree, baseclass_dt, heap=heap)

    for s in incl:
        if s.name != 'baseclass':
            if s.type == 6 and not s.is_proxied():
                inline_dt = tree.find(Compares(s.dt_name)).dt
                subheap   = amass_sendprops(tree, inline_dt)
                heap     += subheap
            else:
                heap.append(s)

    heap = sorted(heap, key=lambda s: s.priority)
    pre  = [s for s in heap if s.priority  < 128]
    post = [s for s in heap if s.priority == 128]
    heap = pre + sorted(post, key=lambda s: s.is_bumped(), reverse=True)

    return [s for s in heap if (s.name, s.origin.name) not in excl]

class Encoder(object):
    def __init__(self, sendprops, exclusions):
        self.sendprops  = sendprops
        self.exclusions = exclusions