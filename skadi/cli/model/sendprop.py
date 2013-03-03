class Sendprop(object):
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
        'ancestral'      : 1 << 11, # most usually baseclass, and excluded when not
        'collapsible'    : 1 << 12, # set if prop is datatable with zero offset that doesn't change pointer (?)
        'coordmp'        : 1 << 13, # like coord, but for multiplayer games
        'coordmplowprec' : 1 << 14, # like coord, but fractional component gets 3 bits, not five
        'coordmpint'     : 1 << 15, # like coord, but rounded to integral boundaries
        'bumped'         : 1 << 18, # nudge property up to just under ones with explicit priority
        'UNKNOWN'        : 0xff00
    }

    def __init__(self, origin, obj):
        self.origin    = origin

        self.type      = obj.type
        self.flags     = obj.flags
        self.name      = obj.var_name
        self.bits      = obj.num_bits
        self.dt_name   = obj.dt_name
        self.priority  = obj.priority

    def named_flags(self):
        return [k for (k,v) in Sendprop.FLAGS.items() if self.flags & v]

    def is_baseclass_ref(self):
        is_ancestral = self.is_ancestral()
        return is_ancestral and self.type == 6 and self.name == 'baseclass'

    def is_excluded(self):
        return self.flags & Sendprop.FLAGS['exclude']

    def is_proxied(self):
        return self.flags & Sendprop.FLAGS['alwaysproxy']

    def is_ancestral(self):
        return self.flags & Sendprop.FLAGS['ancestral']

    def is_bumped(self):
        return self.flags & Sendprop.FLAGS['bumped']
