from galang.types import (Const, Ident, Expr, Lam, Ap, Callable,
                          Iterable, Intrin, List, Dict, Val, MethodName, Map)

# from contextlib import contextmanager

NAMEGEN:int = 0

def mkname(hint:str)->str:
  global NAMEGEN
  acc = f"{hint}_{NAMEGEN}"
  NAMEGEN += 1
  return acc

def num(x:int)->Expr:
  return Val(Const(x))

def ident(x:str)->Expr:
  return Val(Ident(x))

def lam(name:str, body:Callable[[Expr], Expr])->Expr:
  return Lam(name, body(ident(name)))

def ap(func:Expr, arg:Expr)->Expr:
  return Ap(func, arg)

def let_(name, expr:Expr, body:Callable[[Expr], Expr])->Expr:
  return ap(lam(name, body), expr)

def let(expr:Expr, body:Callable[[Expr], Expr])->Expr:
  name = mkname('let')
  return let_(name, expr, body)

def call(func:Expr, args:Iterable[Expr])->Expr:
  acc = func
  for arg in args:
    acc = Ap(acc, arg)
  return acc

def intrin(name:MethodName, args:Dict[str,Expr])->Expr:
  return Intrin(name, Map(args.items()))

