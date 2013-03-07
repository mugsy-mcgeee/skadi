def build_with(dts):
    return Registry(dts)

def dt_sendprops(dts):
    return sum([dt.sendprops for dt in dts], [])

class Compares:
    def __init__(self, dt_name):
        self.dt_name = dt_name

    def __call__(self, other):
        return self.dt_name == other.name

class Registry(object):
    def __init__(self, dts):
        self.dts = dts

    def names(self):
        return [dt.name for dt in self.dts]

    def named(self, dt_name):
        return self.find(Compares(dt_name))

    def sendprops(self):
        dts = [self.named(name) for name in self.names()]
        return sum([dt.sendprops for dt in dts], [])

    def select(self, fn):
        return [dt for dt in self.dts if fn(dt)]

    def find(self, fn):
        gen = (dt for dt in self.dts if fn(dt))
        return next(gen, None)

    def lineage(self, dt):
        lineage  = [dt]
        ancestor = self.named(dt.baseclass)

        while ancestor:
            lineage.append(ancestor)
            ancestor = self.named(dt.baseclass)

        return lineage

    def tInt(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tInt() and not s.fExclude(), ss)

    def tFloat(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tFloat() and not s.fExclude(), ss)

    def tVector(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tVector() and not s.fExclude(), ss)

    def tVectorXY(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tVectorXY() and not s.fExclude(), ss)

    def tString(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tInt() and not s.fExclude(), ss)

    def tArray(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tArray() and not s.fExclude(), ss)

    def tDataTable(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.tDataTable() and not s.fExclude(), ss)

    def flagged(self, flags, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.flags & flags, ss)

    def fExclude(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.fExclude(), ss)

    def fAlwaysProxy(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.fAlwaysProxy(), ss)

    def fCollapsible(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.FCOLLAPSIBLE(), ss)

    def fChangesOften(self, dts=None):
        ss = dt_sendprops(dts) if dts else self.sendprops()
        return filter(lambda s: s.fChangesOften(), ss)
