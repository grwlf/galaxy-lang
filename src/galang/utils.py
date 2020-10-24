from galang.types import Expr, Ident, TMap, Intrin, Lam, Val, Const, Ap
from typing import List, Tuple, Dict, Union, Callable, Set


def idents(e:Expr)->Set[Ident]:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return set()
    elif isinstance(e.val, Ident):
      return set([e.val])
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return idents(e.body)
  elif isinstance(e, Ap):
    return idents(e.func) | idents(e.arg)
  elif isinstance(e, Intrin):
    acc:Set[Ident] = set()
    for a in e.args.values():
      acc |= idents(a)
    return acc
  else:
    raise ValueError(f"Invalid expression {e}")
