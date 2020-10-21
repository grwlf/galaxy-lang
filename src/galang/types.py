from typing import (Union, Callable, List, Iterable, Dict, NamedTuple, Set,
                    Tuple, FrozenSet, TypeVar, Generic, Optional, Tuple)
from dataclasses import dataclass
from immutables import Map

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

MethodName = NamedTuple('MethodName', [('val',str)])

@dataclass(frozen=True)
class Intrin:
  name:MethodName
  args:Map[str,Expr]


M = TypeVar('M')
I = TypeVar('I')

class TMap(Generic[M,I]):
  """ Wrapper of `immutables.Map` with simpler type information. `immutables`
  seems to provide their own typeing, but we want to stay compatible with older
  versions of mypy. """
  def __init__(self, *args, **kwargs)->None:
    self.map = Map(*args, **kwargs)
  def __getitem__(self, key:M)->I:
    return self.map.__getitem__(key)
  def __hash__(self):
    return self.map.__hash__()
  def get(self, key:M, default:Optional[I]=None)->I:
    return self.map.get(key,default)
  def set(self, key:M, val:I)->'TMap[M,I]':
    return TMap(self.map.set(key,val))
  def items(self)->Iterable[Tuple[M,I]]:
    return self.map.items()

def mkmap(d:Optional[Dict[M,I]]=None)->TMap[M,I]:
  return TMap(d if d is not None else {})

Mem = TMap[Ident,Expr]

