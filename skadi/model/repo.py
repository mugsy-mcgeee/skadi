from skadi.model.table import SendTable, RecvTable, fn_excl
from skadi.model.prop import Flag, Type

class Repo(object):
    def __init__(self, send_tables):
        self._send_tables = dict((st.name, st) for st in send_tables)
        self._recv_tables = {}

        print '** Generating receive tables **'
        members = self.st_select(lambda st: st.base() is None)
        self._rt_populate(members)

    def st_select(self, fn):
        return [st for st_name, st in self._send_tables.items() if fn(st)]

    def st_named(self, name):
        if name is None:
            return None
        return self._send_tables[name]

    def st_find(self, fn):
        gen = (st for st_name, st in self._send_tables.items() if fn(st))
        return next(gen, None)

    def st_props(self, fn=None, scope=None):
        if scope is None:
            scope = self._send_tables.values()
        pp = [st.props(fn=fn) for st in scope]
        return sum(pp, [])

    def rt_named(self, name):
        if name is None:
            return RecvTable(None, [])
        return self._recv_tables[name]

    def rt_select(self, fn):
        return [rt for rt_name, rt in self._recv_tables.items() if fn(rt)]

    def rt_find(self, fn):
        gen = (rt for rt in self._recv_tables.values() if fn(rt))
        return next(gen, None)

    def rt_props(self, fn=None, scope=None):
        if scope is None:
            scope = self._recv_tables.values()
        pp = [rt.props(fn=fn) for rt in scope]
        return sum(pp, [])

    def _rt_populate(self, members, depth=0):
        for st in members:
            flatprops = st.flatten(self)

            pad = '  ' * depth
            print '{0}{1}'.format(pad, st.name)
            for i, p in enumerate(filter(fn_excl, st.props())):
                print '  {0}{1}: {2}'.format(pad, str(i).rjust(2), str(p))

            for i, p in enumerate(flatprops):
                print '{0}->{1}: {2}'.format(pad, str(i).rjust(3), str(p))

            members = self.st_select(lambda st2: st2.base() == st.name)
            self._rt_populate(members, depth=depth+1)
