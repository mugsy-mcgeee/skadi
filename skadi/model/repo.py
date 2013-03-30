from skadi.model.table import SendTable, RecvTable
from skadi.model.prop import Flag, Type

class Repo(object):
    def __init__(self, tables):
        self._tables = dict((t.name(), t) for t in tables)

    def select(self, fn):
        return [t for t_name, t in self._tables.items() if fn(t)]

    def named(self, name):
        if name is None:
            return None
        return self._tables[name]

    def flatten(self, st, st_excl=None, depth=0):
        pp_flat = []
        st_excl = st_excl or st
        st      = st - st_excl

        for p in st.inclusions():
            if p.type == Type.DATATABLE and p.flags & Flag.COLLAPSIBLE:
                st      = self.named(p.st_name)
                pp_flat = self.flatten(st, st_excl=st_excl, depth=depth+1) + pp_flat
            elif p.type == Type.DATATABLE:
                st      = self.named(p.st_name)
                pp_flat = pp_flat + self.flatten(st, st_excl=st_excl, depth=depth+1)
            else:
                pp_flat.append(p)

        return pp_flat

    def find(self, fn):
        gen = (t for t_name, t in self._tables.items() if fn(t))
        return next(gen, None)

    def props(self, fn=None, scope=None):
        if scope is None:
            scope = self._tables.values()
        props = [t.props(fn=fn) for t in scope]
        return sum(props, [])
