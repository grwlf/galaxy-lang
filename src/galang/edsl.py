from galang.types import (Ident, Term, Expr, Let, Ap, Callable, Iterable)


def let(name:str, val:Expr, body:Callable[[Expr], Expr])->Expr:
  return Let(name, val, body(Ident(name)))


def call(func:Expr, args:Iterable[Expr])->Expr:
  acc=func
  for arg in args:
    acc=Ap(acc, arg)
  return acc



