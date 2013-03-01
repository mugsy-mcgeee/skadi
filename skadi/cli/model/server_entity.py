class Property(object):
    FLAGS = {
        'unsigned'       : 1 <<  0, # unsigned integer
        'coord'          : 1 <<  1, # fp/vector treated as world coord (bit count ignored)
        'noscale'        : 1 <<  2, # for fp, take as-is value
        'rounddown'      : 1 <<  3, # for fp, limit high value to range minus one bit unit
        'roundup'        : 1 <<  4, # for fp, limit low  value to range minus one bit unit
        'normal'         : 1 <<  5, # vector is treated like a normal (valid only for vectors)
        'exclude'        : 1 <<  6, # this prop points to another prop to be excluded
        'xyze'           : 1 <<  7, # use XYZ/exponent encoding for vectors
        'insidearray'    : 1 <<  8, # prop is inside array ("shouldn't be put in flattened prop list" (?))
        'alwaysproxy'    : 1 <<  9, # set for data table props using a default proxy type
        'changesoften'   : 1 << 10, # set for fields set often so they get a small index in sendtable
        'classref'       : 1 << 11, # prop is member of a vector
        'collapsible'    : 1 << 12, # set if prop is datatable with zero offset that doesn't change pointer (?)
        'coordmp'        : 1 << 13, # like coord, but for multiplayer games
        'coordmplowprec' : 1 << 14, # like coord, but fractional component gets 3 bits, not five
        'coordmpint'     : 1 << 15, # like coord, but rounded to integral boundaries
        'UNKNOWN'        : 0xff00
    }

    def __init__(self, origin, obj):
        self.origin    = origin

        self.type      = obj.type
        self.flags     = obj.flags
        self.name      = obj.var_name
        self.bits      = obj.num_bits
        self.data_type = obj.dt_name
        self.priority  = obj.priority

    def named_flags(self):
        return [k for (k,v) in Property.FLAGS.items() if self.flags & v]

class ServerEntity(object):
    def __init__(self, obj):
        relevant = [p.dt_name for p in obj.props if p.var_name == 'baseclass']
        self.name       = obj.net_table_name
        self.baseclass  = None if not relevant else relevant[0]
        self.properties = [Property(self, p) for p in obj.props]
        self.encoded    = obj.needs_decoder
