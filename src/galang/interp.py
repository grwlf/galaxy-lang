from typing import Union, Optional, Dict, List, Any, Callable, NamedTuple
from dataclasses import dataclass
from numpy import ndarray
from copy import copy, deepcopy

from galang.types import Expr, Ident, Ap, Val, Const, Lam, Intrin

import numpy as np

IExpr = Union['IVal', 'IAp', 'ILam']

@dataclass(frozen=True)
class IVal:
  val:Union[int, str, ndarray]

@dataclass(frozen=True)
class IAp:
  func:IExpr
  arg:IExpr

@dataclass(frozen=True)
class ILam:
  name:str
  body:Expr


LibEntry = NamedTuple('LibEntry', [('name',str),
                                   ('args',List[str]),
                                   ('impl',Callable[[Dict[str,IExpr]],IExpr])])

Lib = Dict[str,LibEntry]

Mem = Dict[Ident,IExpr]

def interp(expr:Expr, lib:Lib, mem:Mem)->IExpr:
  m:Mem = copy(mem) if mem is not None else {}
  if isinstance(expr, Val):
    if isinstance(expr.val, Ident):
      return m[expr.val]
    elif isinstance(expr.val, Const):
      return IVal(expr.val.const)
    else:
      raise ValueError(f"Invalid value {expr}")
  elif isinstance(expr, Ap):
    func = interp(expr.func, lib, m)
    arg = interp(expr.arg, lib, m)
    if isinstance(func, ILam):
      m[Ident(func.name)] = arg
      return interp(func.body, lib, m)
    else:
      raise ValueError(f"Invalid callable {func}")
  elif isinstance(expr, Lam):
    return ILam(expr.name, expr.body)
  elif isinstance(expr, Intrin):
    libentry = lib[expr.name]
    iargs = {}
    for aname,aexpr in expr.args.items():
      iargs.update({aname: interp(aexpr,lib,m)})
    return libentry.impl(iargs)
  else:
    raise ValueError(f"Invalid expression {expr}")


