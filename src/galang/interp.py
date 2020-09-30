from typing import Union, Optional, Dict, List, Any
from dataclasses import dataclass
from numpy import ndarray
from galang.types import Expr, Ident, Let, Ap
from copy import copy, deepcopy

import numpy as np

Val = Union['VVal', 'VLam', 'VAp']

@dataclass(frozen=True)
class VCallable:
  name:str
  args:List[str]

@dataclass(frozen=True)
class VVal:
  val:Union[VCallable, int, str, ndarray]

@dataclass(frozen=True)
class VLam:
  name:str
  body:Val

@dataclass(frozen=True)
class VAp:
  func:Val
  arg:Val


@dataclass(frozen=True)
class LibRecord:
  func:Any
  anames:List[str]


Lib = Dict[str, LibRecord]

LIB:Lib = {
  # https://numpy.org/doc/stable/reference/generated/numpy.transpose.html#numpy.transpose
  'transpose': LibRecord(np.transpose, ['input']),
  # https://numpy.org/doc/stable/reference/generated/numpy.concatenate.html
  'concat': LibRecord(np.concatenate, []),
  # https://numpy.org/doc/stable/reference/generated/numpy.split.html
  'split': LibRecord(np.split, [])
}


def interp(expr:Expr,
           letmem:Optional[Dict[Ident,Val]]=None,
           appmem:Optional[Dict[Ident,Val]]=None,
           lib:Lib=LIB)->Val:
  lib=deepcopy(lib)
  lm:Dict[Ident,Val] = copy(letmem) if letmem is not None else {}
  am:Dict[Ident,Val] = copy(appmem) if appmem is not None else {}
  if isinstance(expr, Ident):
    return lm[expr]
  elif isinstance(expr, Ap):
    vap = interp(expr.func, lm, am)
    varg = interp(expr.arg, lm, am)
    if isinstance(vap, VLam):
      am[Ident(vap.name)] = varg
      return interp(vap.body, lm, am)
    elif isinstance(vap, VVal):
      assert isinstance(vap.val, VCallable)
      lr=LIB[vap.val.name]
      assert len(list(am.values()))==len(lr.anames)
      return VVal(lr.func(**am))
    else:
      raise ValueError(f"Invalid callable {vap}")
  elif isinstance(expr, Let):
    lm[Ident(expr.name)] = expr.expr
    return interp(expr.body, lm, am)
  else:
    raise ValueError(f"Invalid expression {expr}")


