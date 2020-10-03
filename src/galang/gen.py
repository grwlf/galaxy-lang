from galang.types import Expr
from galang.edsl import intrin, lam, let, ident, nnum
from typing import List

def genexpr(nargs:int)->Expr:
  """ Generate lambda-expression with `nargs` arguments """

  def _genbody(avail:List[Expr]):
    return nnum(0)

  def _genlam(avail:List[Expr])->Expr:
    def _f(x):
      avail2 = avail + [x]
      return _genbody(avail2) if len(avail2)==nargs else _genlam(avail2)
    return lam(f'arg-{nargs}', _f)

  return _genlam([])
