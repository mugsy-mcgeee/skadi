from skadi.model.prop import Prop, Flag, Type

fn_excl          = lambda p: p.flags & Flag.EXCLUDE
fn_incl          = lambda p: p.flags ^ Flag.EXCLUDE
fn_prioritized   = lambda p: p.priority < 128
fn_by_priority   = lambda p: p.priority
fn_deprioritized = lambda p: p.priority == 128
fn_by_type       = lambda p: p.type

class SendTable(object):
    def __init__(self, obj):
        self.name       = obj.net_table_name
        self.is_leaf    = obj.needs_decoder
        self.is_last    = obj.is_end
        self._props     = [Prop(self.name, p) for p in obj.props]
        self._flatprops = None

    def base(self):
        gen = (p for p in self.props(lambda p: p.name == 'baseclass'))
        p   = next(gen, None)
        return p.st_name if p else None

    def props(self, fn=None):
        pp = [p for p in self._props]
        return filter(fn, pp) if fn else pp

    def flatten(self, repo, excl=None, coll=False, depth=0):
        pp_flat = []
        pp_incl = filter(fn_incl, self.props())
        pp_excl = filter(fn_excl, self.props())

        if excl is None:
            excl = map(lambda p: (p.st_name, p.name), pp_excl)
        else:
            excl = map(lambda p: (p.st_name, p.name), pp_excl) + excl

        _excl = []

        for p in pp_incl:
            if (p.origin, p.name) not in excl:
                if p.type == Type.DATATABLE and p.flags & Flag.COLLAPSIBLE:
                    st      = repo.st_named(p.st_name)
                    pp_flat = st.flatten(repo, excl=excl, depth=depth+1) + pp_flat
                elif p.type == Type.DATATABLE:
                    st      = repo.st_named(p.st_name)
                    pp_flat = pp_flat + st.flatten(repo, excl=excl, depth=depth+1)
                else:
                    pp_flat.append(p)
            else:
                _excl.append((p.origin, p.name))

        diff = set(excl) - set(_excl)
        if diff:
            print 'at level %s' % self.name
            for p in diff:
                if p[0] == self.name:
                    print "NEXCL: %s.%s" % p

        return sorted(pp_flat, key=fn_by_priority)

class RecvTable(object):
    def __init__(self, name, props):
        self.name  = name
        self.props = props
