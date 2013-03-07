
def enum(**enums):
    _enum = type('Enum', (), enums)
    _enum.__keys__ = enums.keys()
    return _enum

Flag = enum(
    UNSIGNED         = ('unsigned'        , 1 <<  0), # unsigned integer
    COORD            = ('coord'           , 1 <<  1), # float/vec is world coord (ignores bit count)
    NOSCALE          = ('noscale'         , 1 <<  2), # take float value as is
    ROUNDDOWN        = ('rounddown'       , 1 <<  3), # limit float high val to (range - 1 bit-unit)
    ROUNDUP          = ('roundup'         , 1 <<  4), # limit float low  val to (range - 1 bit-unit)
    NORMAL           = ('normal'          , 1 <<  5), # treat value as normal (valid only for vector)
    EXCLUDE          = ('exclude'         , 1 <<  6), # this prop indicates exclusion of another
    XYZE             = ('xyze'            , 1 <<  7), # use "XYZ/Exponent" encoding for vectors (?)
    INSIDEARRAY      = ('insidearray'     , 1 <<  8), # in array (doesn't go in flat props)
    PROXYALWAYS      = ('proxyalways'     , 1 <<  9), # always proxy all data to all clients
    VECTORELEM       = ('vectorelem'      , 1 << 10), # vector
    COLLAPSIBLE      = ('collapsible'     , 1 << 11), # refers to another datatable with no changes
    COORDMP          = ('coordmp'         , 1 << 12), # COORD, but special treatment for multiplayer
    COORDMPLOWPREC   = ('coordmplowprec'  , 1 << 13), # above, but frac gets 3 bits
    COORDMPINT       = ('coordmpint'      , 1 << 14), # above, but round to int
    CELLCOORD        = ('cellcoord'       , 1 << 15), # COORD, but non-neg (bits have maxval)
    CELLCOORDLOWPREC = ('cellcoordlowprec', 1 << 16), # above, but frac gets 3 bits
    CELLCOORDINT     = ('cellcoordint'    , 1 << 17), # above, but round to int
    CHANGESOFTEN     = ('changesoften'    , 1 << 18)  # move to top of sendtable for low prop index
)

Type = enum(
    INT       = ('int'      , 0),
    FLOAT     = ('float'    , 1),
    VECTOR    = ('vector'   , 2),
    VECTORXY  = ('vectorxy' , 3),
    STRING    = ('string'   , 4),
    ARRAY     = ('array'    , 5), # an array of primitives (not datatables)
    DATATABLE = ('datatable', 6),
    INT64     = ('int64'    , 7)
)

class Sendprop(object):
    def __init__(self, dt, obj):
        self.origin    = dt
        self.name      = obj.var_name

        self.type      = obj.type
        self.flags     = obj.flags
        self.priority  = obj.priority
        self.bits      = obj.num_bits
        self.dt_name   = obj.dt_name

    def __str__(self):
        origin, name = self.origin.name, self.name

        type     = self.named_type()
        flags    = ','.join(self.named_flags()) if self.flags else '*'
        priority = self.priority if self.priority < 128       else '*'
        bits     = self.bits     if self.bits                 else '*'
        dt_name  = self.dt_name  if self.dt_name              else '*'

        repr = "<{0}.{1} t:{2} f:{3} p:{4} b:{5}>"

        return repr.format(origin, name, type, flags, priority, bits)

    def named_type(self):
        k, d = (Type.__keys__, Type.__dict__)
        gen  = (d[key][0] for key in k if d[key][1] == self.type)
        return gen.next()

    def named_flags(self):
        k, d = (Flag.__keys__, Flag.__dict__)
        return [d[key][0] for key in k if d[key][1] & self.flags]

    def tInt(self):
        return self.type == Type.INT[1]

    def tFloat(self):
        return self.type == Type.FLOAT[1]

    def tVector(self):
        return self.type == Type.VECTOR[1]

    def tVectorXY(self):
        return self.type == Type.VECTORXY[1]

    def tString(self):
        return self.type == Type.STRING[1]

    def tArray(self):
        return self.type == Type.ARRAY[1]

    def tDataTable(self):
        return self.type == Type.DATATABLE[1]

    def tInt64(self):
        return self.type == Type.INT64[1]

    def fExclude(self):
        return (self.flags & Flag.EXCLUDE[1])

    def fAlwaysProxy(self):
        return (self.flags & Flag.PROXYALWAYS[1])

    def fCollapsible(self):
        return (self.flags & Flag.COLLAPSIBLE[1])

    def fChangesOften(self):
        return (self.flags & Flag.CHANGESOFTEN[1])
