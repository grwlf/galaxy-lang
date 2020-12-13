from galang.types import Lib, LibEntry, IVal, MethodName, TMap, IError, IExpr

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

def mn(n:str)->MethodName:
  return MethodName(n)

lib:Lib = TMap({
  mn('transpose'): LibEntry(mn('transpose'), ['a'], _transpose),
  mn('concat'): LibEntry(mn('concat'), ['a','b'], _concat),
  mn('split'): LibEntry(mn('split'), ['a'], _split)
})
