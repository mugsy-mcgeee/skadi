from skadi.model.sendprop import Sendprop, Type, Flag

class DT(object):
    def __init__(self, obj):
        baseclass = (p.dt_name for p in obj.props if p.var_name == 'baseclass')
        self.baseclass = next(baseclass, None)
        self.name      = obj.net_table_name
        self.encoded   = obj.needs_decoder

        self._sendprops = [Sendprop(self, p) for p in obj.props]

    def sendprops(self, t=None, f=None):
        ss = self._sendprops

        if t:
            by_type  = lambda s: s.type == t
            ss       = filter(by_type, ss)
        if f:
            by_flags = lambda s: s.flags & f
            ss       = filter(by_flags, ss)

        return ss

    def inclusions(self):
        return [s for s in self.sendprops() if s.flags ^ Flag.EXCLUDE]

    def exclusions(self):
        return [s for s in self.sendprops() if s.flags & Flag.EXCLUDE]
