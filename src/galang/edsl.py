from galang.types import (Const, Ident, Expr, Lam, Ap, Callable,
                          Iterable, Intrin, List, Dict, Val)

# from contextlib import contextmanager

NAMEGEN:int = 0

def mkname(hint:str)->str:
  global NAMEGEN
  acc = f"{hint}_{NAMEGEN}"
  NAMEGEN += 1
  return acc

def nnum(x:int)->Expr:
  return Val(Const(x))

def ident(x:str)->Expr:
  return Val(Ident(x))

def lam(name:str, body:Callable[[Expr], Expr])->Expr:
  return Lam(name, body(ident(name)))

def ap(func:Expr, arg:Expr)->Expr:
  return Ap(func, arg)

def let(expr:Expr, body:Callable[[Expr], Expr])->Expr:
  name = mkname('let')
  return ap(lam(name, body), expr)

# def call(name:str, args:Iterable[Expr])->Expr:
#   acc = Ident(name)
#   for arg in args:
#     acc = Ap(acc, arg)
#   return acc

def intrin(name:str, args:Dict[str,Expr])->Expr:
  return Intrin(name, args)
