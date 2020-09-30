from galang.types import (Const, Ident, Expr, Let, Ap, Callable,
                          Iterable)

# from contextlib import contextmanager

NAMEGEN:int = 0

def mkname(hint:str)->str:
  global NAMEGEN
  acc = f"{hint}_{NAMEGEN}"
  NAMEGEN += 1
  return acc

def num(x:int)->Expr:
  return Const(x)

def let(name:str, val:Expr, body:Callable[[Expr], Expr])->Expr:
  return Let(name, val, body(Ident(name)))

def wlet(val:Expr, body:Callable[[Expr], Expr])->Expr:
  return let(mkname('wlet'), val, body)

# @contextmanager
# def clet(name:str, val:Expr):
#   body = yield Ident(name)
#   return Let(name, val, body)

def call(func:Expr, args:Iterable[Expr])->Expr:
  acc=func
  for arg in args:
    acc=Ap(acc, arg)
  return acc


