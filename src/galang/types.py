from typing import Union, Callable, List, Iterable
from dataclasses import dataclass

Expr = Union['Const', 'Ident', 'Ap', 'Let']

@dataclass(frozen=True, eq=True)
class Const:
  val:int

@dataclass(frozen=True, eq=True)
class Ident:
  name:str
  # nargs:int

@dataclass(frozen=True)
class Ap:
  func:Expr
  arg:Expr

@dataclass(frozen=True)
class Let:
  name:str
  expr:Expr
  body:Expr

