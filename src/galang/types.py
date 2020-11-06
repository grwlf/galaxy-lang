from typing import (Union, Callable, List, Iterable, Dict, NamedTuple, Set,
                    Tuple, FrozenSet, TypeVar, Generic, Optional, Tuple)
from dataclasses import dataclass
# from immutables import Map
from frozenordereddict import FrozenOrderedDict


M = TypeVar('M')
I = TypeVar('I')

class TMap(Generic[M,I]):
  """ Wrapper of `immutables.Map` with simpler type information. `immutables`
  seems to provide their own typeing, but we want to stay compatible with older
  versions of mypy. """
  def __init__(self, *args, **kwargs)->None:
    self.dict = FrozenOrderedDict(*args, **kwargs)
  def __getitem__(self, key:M)->I:
    return self.dict.__getitem__(key)
  def __hash__(self):
    return self.dict.__hash__()
  def get(self, key:M, default:Optional[I]=None)->I:
    return self.dict.get(key,default)
  def set(self, key:M, val:I)->'TMap[M,I]':
    return TMap(self.dict.copy({key:val}))
  def items(self)->Iterable[Tuple[M,I]]:
    return self.dict.items()
  def values(self)->Iterable[I]:
    return self.dict.values()
  def keys(self)->Iterable[M]:
    return self.dict.keys()
  def __eq__(self,other):
    return self.dict==other.dict

def mkmap(d:Optional[Dict[M,I]]=None)->TMap[M,I]:
  return TMap(d if d is not None else {})


@dataclass(frozen=True, eq=True)
class Const:
  const:int

@dataclass(frozen=True, eq=True)
class Ref:
  name:str

Expr = Union['Val', 'Lam', 'Ap', 'Let', 'Intrin']

@dataclass(frozen=True, eq=True)
class Val:
  val:Union[Const, Ref]

@dataclass(frozen=True)
class Ap:
  func:Expr
  arg:Expr

@dataclass(frozen=True)
class Let:
  """ Here: Let is more a syntactic sugar for `Ap (Lam ref body) expr` """
  ref:Ref
  expr:Expr
  body:Expr

@dataclass(frozen=True)
class Lam:
  name:str # Pattern
  body:Expr # May refer to `Ref(name)`

MethodName = NamedTuple('MethodName', [('val',str)])

@dataclass(frozen=True)
class Intrin:
  name:MethodName
  args:TMap[str,Expr]


Mem = TMap[Ref,Expr]

