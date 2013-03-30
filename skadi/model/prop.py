
def enum(**enums):
    _enum = type('Enum', (), enums)
    _enum._enums = enums
    return _enum

P_DEFAULT      = 128
P_CHANGESOFTEN = 64

Flag = enum(
    UNSIGNED         = 1 <<  0, # unsigned integer
    COORD            = 1 <<  1, # float/vec is world coord (ignores bit count)
    NOSCALE          = 1 <<  2, # take float value as is
    ROUNDDOWN        = 1 <<  3, # limit float high val to (range - 1 bit-unit)
    ROUNDUP          = 1 <<  4, # limit float low  val to (range - 1 bit-unit)
    NORMAL           = 1 <<  5, # treat value as normal (valid only for vector)
    EXCLUDE          = 1 <<  6, # this prop indicates exclusion of another
    XYZE             = 1 <<  7, # use "XYZ/Exponent" encoding for vectors (?)
    INSIDEARRAY      = 1 <<  8, # in array (doesn't go in flat props)
    PROXYALWAYS      = 1 <<  9, # always proxy all data to all clients
    VECTORELEM       = 1 << 10, # vector
    COLLAPSIBLE      = 1 << 11, # refers to another datatable with no changes
    COORDMP          = 1 << 12, # COORD, but special treatment for multiplayer
    COORDMPLOWPREC   = 1 << 13, # above, but frac gets 3 bits
    COORDMPINT       = 1 << 14, # above, but round to int
    CELLCOORD        = 1 << 15, # COORD, but non-neg (bits have maxval)
    CELLCOORDLOWPREC = 1 << 16, # above, but frac gets 3 bits
    CELLCOORDINT     = 1 << 17, # above, but round to int
    CHANGESOFTEN     = 1 << 18, # move to top of sendtable for low prop index
    MYSTERY          = 1 << 19  # a magician told me about this
)

Type = enum(
    INT       = 0,
    FLOAT     = 1,
    VECTOR    = 2,
    VECTORXY  = 3,
    STRING    = 4,
    ARRAY     = 5, # an array of primitives (not datatables)
    DATATABLE = 6,
    INT64     = 7
)

class Prop(object):
    def __init__(self, origin, obj):
        self.origin   = origin
        self.name     = obj.var_name
        self.type     = obj.type
        self.flags    = obj.flags
        self.elements = obj.num_elements
        self.bits     = obj.num_bits
        self.st_name  = obj.dt_name

        if obj.priority == P_DEFAULT and self.flags & Flag.CHANGESOFTEN:
            self.priority = P_CHANGESOFTEN
        else:
            self.priority = obj.priority

    def __str__(self):
        origin, name = self.origin, self.name

        type     = self._named_type()
        flags    = ','.join(self._named_flags()) if self.flags else '*'
        priority = self.priority if self.priority < 128 else '*'
        bits     = self.bits     or '*'
        elements = self.elements or '*'
        st_name  = self.st_name  or '*'

        repr = "<{0}.{1} t:{2} f:{3} p:{4} b:{5} e:{6} o:{7}>"

        return repr.format(origin, name, type, flags, priority, bits, elements, st_name)

    def _named_type(self):
        for k, v in Type._enums.items():
            if self.type == v:
                return k.lower()
        return None

    def _named_flags(self):
        named_flags = []
        for k, v in Flag._enums.items():
            if self.flags & v:
                named_flags.append(k.lower())
        return named_flags
