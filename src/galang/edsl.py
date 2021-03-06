from galang.types import (Const, Ref, Expr, Lam, Ap, Callable, Tuple, Iterable,
                          Intrin, List, Dict, Val, MethodName, TMap, Let)

from collections import OrderedDict
# from contextlib import contextmanager

NAMEGEN:int = 0

def mkname(hint:str)->str:
  global NAMEGEN
  acc = f"{hint}_{NAMEGEN}"
  NAMEGEN += 1
  return acc

def num(x:int)->Expr:
  return Val(Const(int(x)))

def ref(x:str)->Expr:
  return Val(Ref(str(x)))

def lam(name:str, body:Callable[[Expr], Expr])->Expr:
  return Lam(str(name), body(ref(name)))

def ap(func:Expr, arg:Expr)->Expr:
  return Ap(func, arg)

def let_(name:str, expr:Expr, body:Callable[[Expr], Expr])->Expr:
  return Let(Ref(str(name)), expr, body(ref(name)))

def let(expr:Expr, body:Callable[[Expr], Expr])->Expr:
  name = mkname('let')
  return let_(name, expr, body)

def call(func:Expr, args:Iterable[Expr])->Expr:
  acc = func
  for arg in args:
    acc = Ap(acc, arg)
  return acc

def intrin(name:MethodName, args:List[Tuple[str,Expr]])->Expr:
  acc = OrderedDict()
  for (k,v) in args:
    acc[str(k)] = v
  return Intrin(name, TMap(acc))

