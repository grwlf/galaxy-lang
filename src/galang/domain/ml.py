from galang.interp import Lib, LibEntry, IVal

# mem:Mem = {
#   # https://numpy.org/doc/stable/reference/generated/numpy.transpose.html#numpy.transpose
#   Ident('transpose'): lam('transpose_a', lambda a:
#                           intrin('transpose',{'a':a})),
#   # https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html
#   Ident('concat'):    lam('concat_a', lambda a:
#                       lam('concat_b', lambda b:
#                           intrin('concat', {'a':a,'b':b}))),
#   # https://numpy.org/doc/stable/reference/generated/numpy.split.html
#   Ident('split'):     lam('split_a', lambda a:
#                           intrin('split', {'a':a})),
# }


def _transpose(args):
  pass

def _concat(args):
  pass

def _split(args):
  pass

lib:Lib = {
  'transpose': LibEntry('transpose', ['a'], _transpose),
  'concat': LibEntry('concat', ['a','b'], _concat),
  'split': LibEntry('split', ['a'], _split)
}
