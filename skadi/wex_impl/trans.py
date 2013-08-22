import skadi.wex_impl as wex_impl
from skadi.engine import world


class NotFound(Exception):
  pass


def to_datatype(prop, src_val, stream):
  if prop.is_handle:
    try:
      src_val = stream.world.fetch_recv_table(src_val).dt
    except KeyError:
      raise NotFound('eHandle {} not found for prop {}'.format(src_val, prop.prop_key))
  else:
    raise Exception('src_val={} and isn\'t handle. What is it then?'.format(src_val))

  return src_val
