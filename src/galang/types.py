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
  def __len__(self):
    return len(self.dict)
  def __repr__(self):
    return f"TMap({self.dict.__repr__()})"

def mkmap(d:Optional[Dict[M,I]]=None)->TMap[M,I]:
  return TMap(d if d is not None else {})

def mergemap(a:TMap[M,I], b:TMap[M,I], f:Callable[[I,I],I])->TMap[M,I]:
  d={}
  ak=set(a.keys())
  bk=set(b.keys())
  for k in a.keys():
    if k in bk:
      d[k]=f(a[k],b[k])
      bk-=set([k])
    else:
      d[k]=a[k]
  for k in b.keys():
    if k not in ak:
      d[k]=b[k]
  return TMap(d)

#  _____
# | ____|_  ___ __  _ __
# |  _| \ \/ / '_ \| '__|
# | |___ >  <| |_) | |
# |_____/_/\_\ .__/|_|
#            |_|

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


#  ___ _____
# |_ _| ____|_  ___ __  _ __
#  | ||  _| \ \/ / '_ \| '__|
#  | || |___ >  <| |_) | |
# |___|_____/_/\_\ .__/|_|
#                |_|


IExpr = Union['IVal', 'IAp', 'ILam', 'IError']

@dataclass(frozen=True)
class IError:
  msg:str

@dataclass(frozen=True)
class IVal:
  val:Union[int, str]

@dataclass(frozen=True)
class IAp:
  func:IExpr
  arg:IExpr

@dataclass(frozen=True)
class ILam:
  name:str
  body:Expr

LibEntry = NamedTuple('LibEntry', [('name',MethodName),
                                   ('argnames',List[str]),
                                   ('impl',Callable[[Dict[str,IExpr]],IExpr])])

Lib = TMap[MethodName,LibEntry]

IMem = TMap[Ref,IExpr]


#  _____                           _
# | ____|_  ____ _ _ __ ___  _ __ | | ___
# |  _| \ \/ / _` | '_ ` _ \| '_ \| |/ _ \
# | |___ >  < (_| | | | | | | |_) | |  __/
# |_____/_/\_\__,_|_| |_| |_| .__/|_|\___|
#                           |_|

@dataclass(frozen=True, eq=True)
class Example:
  inp:IMem
  expr:Expr
  out:IExpr




