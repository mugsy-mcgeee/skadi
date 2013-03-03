from skadi.cli.model.sendprop import Sendprop

class DT(object):
    def __init__(self, obj):
        baseclass = (p.dt_name for p in obj.props if p.var_name == 'baseclass')
        self.baseclass = next(baseclass, None)

        self.name      = obj.net_table_name
        self.sendprops = [Sendprop(self, p) for p in obj.props]
        self.encoded   = obj.needs_decoder
