class ServerEntity(object):
    def __init__(self, obj):
        relevant = [p.dt_name for p in obj.props if p.var_name == 'baseclass']
        self.name      = obj.net_table_name
        self.baseclass = None if not relevant else relevant[0]
