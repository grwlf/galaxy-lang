from typing import Union, Callable, List, Iterable, Dict
from dataclasses import dataclass

@dataclass(frozen=True, eq=True)
class Const:
  const:int

@dataclass(frozen=True, eq=True)
class Ident:
  ident:str

Expr = Union['Val', 'Lam', 'Ap', 'Intrin']

@dataclass(frozen=True, eq=True)
class Val:
  val:Union[Const, Ident]

@dataclass(frozen=True)
class Ap:
  func:Expr
  arg:Expr

@dataclass(frozen=True)
class Lam:
  name:str # Pattern
  body:Expr # May refer to `Ident(name)`

@dataclass(frozen=True)
class Intrin:
  name:str
  args:Dict[str,Expr]
