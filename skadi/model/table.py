from skadi.model.prop import Prop, Flag, Type

fn_incl     = lambda p: p.flags ^ Flag.EXCLUDE
fn_excl     = lambda p: p.flags & Flag.EXCLUDE
fn_as_tuple = lambda p: (p.st_name, p.name)

class Proplist(object):
    def __init__(self, props):
        self._props = props

    def props(self, fn=None):
        return filter(fn, self._props) if fn else self._props

    def inclusions(self, fn=None):
        base = self.props(fn=fn_incl)
        return filter(fn, base) if fn else base

    def exclusions(self):
        return map(fn_as_tuple, self.props(fn=fn_excl))

    def __sub__(self, other):
        excl = other.exclusions()
        diff = self.inclusions(lambda p: (p.st_name, p.name) not in excl)
        return Proplist(diff)

class Table(object):
    delegated = ('props', 'inclusions', 'exclusions')

    def __init__(self, name, proplist):
        self._name     = name
        self._proplist = proplist

    def __getattribute__(self, name):
        if name in Table.delegated:
            return self.proplist().__getattribute__(name)
        else:
            return object.__getattribute__(self, name)

    def name(self):
        return self._name

    def proplist(self):
        return self._proplist

class SendTable(Table):
    def __init__(self, name, proplist, is_leaf=False):
        super(SendTable, self).__init__(name, proplist)
        self._is_leaf = is_leaf

    def __sub__(self, other):
        proplist = self.proplist() - other.proplist()
        return SendTable(self.name(), proplist, is_leaf=self.is_leaf())

    def base(self):
        gen = (p for p in self.props(lambda p: p.name == 'baseclass'))
        p   = next(gen, None)
        return p.st_name if p else None

    def is_leaf(self):
        return self._is_leaf

class RecvTable(Table):
    def __init__(self, name, proplist):
        super(RecvTable, self).__init__(name, proplist)
