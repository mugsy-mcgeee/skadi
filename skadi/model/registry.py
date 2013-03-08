from skadi.model.sendprop import Flag, Type

def build_with(dts):
    return Registry(dts)

class VerifiesEncoded:
    def __call__(self, other):
        return other.encoded

class Compares:
    def __init__(self, dt_name):
        self.dt_name = dt_name

    def __call__(self, other):
        return self.dt_name == other.name

class Registry(object):
    def __init__(self, dts):
        self.dts = dts

    def encoded(self):
        return self.select(lambda dt: dt.encoded)

    def not_encoded(self):
        return self.select(lambda dt: not dt.encoded)

    def named(self, dt_name):
        return self.find(Compares(dt_name))

    def flattened(self, dt, exclusions=None):
        lineage   = self._lineate(dt)
        flatprops = []

        if exclusions is None:
            exclusions = [self._exclusions(_dt) for _dt in lineage]
            exclusions = sum(exclusions, []) # flatten

        for _dt in lineage:
            for s in _dt.inclusions():
                if s not in exclusions:
                    __dt = self.named(s.dt_name)
                    if s.type == Type.DATATABLE and __dt not in lineage:
                        flatprops = self.flattened(__dt, exclusions) + flatprops
                    elif s.flags ^ Flag.COLLAPSIBLE:
                        flatprops.append(s)

        flatprops = sorted(flatprops, key=lambda s: s.priority)

        return flatprops

    def select(self, fn):
        return [dt for dt in self.dts if fn(dt)]

    def find(self, fn):
        gen = (dt for dt in self.dts if fn(dt))
        return next(gen, None)

    def sendprops(self, via=None, t=None, f=None):
        if via is None:
            via = self.dts
        ss = [dt.sendprops(t=t, f=f) for dt in via]
        return sum(ss, [])

    def _lineate(self, dt):
        lineage  = [dt]
        ancestor = self.named(dt.baseclass)

        while ancestor:
            lineage.append(ancestor)
            ancestor = self.named(ancestor.baseclass)

        return lineage[::-1]

    def _exclusions(self, dt):
        exclusions = []

        for s in dt.exclusions():
            s_name = s.name
            dt     = self.named(s.dt_name)
            gen    = (s for s in dt.sendprops() if s.name == s_name)
            try:
                exclusions.append(gen.next())
            except:
                print "No sendprop for {0}.{1}".format(s.dt_name, s_name)

        return exclusions
