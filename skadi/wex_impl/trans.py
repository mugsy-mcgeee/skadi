import skadi.wex_impl as wex_impl

def to_datatype(prop, src_val, stream):
  if prop.is_handle:
    src_val,_ = wex_impl.from_ehandle(src_val)

  if src_val != 2047:
    index = str(stream.entities[src_val][0])
    src_val = stream.recv_tables[index]
  else:
    src_val = 'Undefined'

  return src_val
