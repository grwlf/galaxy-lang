from sys import maxsize
from galang.types import Lib, LibEntry, IVal, MethodName, TMap, IError, IExpr
from math import sqrt


def _add(a,b)->IExpr:
  return IVal(a+b)

def _mul(a,b)->IExpr:
  return IVal(a*b)

def _div(a,b)->IExpr:
  try:
    return IVal(a//b)
  except ZeroDivisionError:
    return IError('Division by zero')

def _neg(a)->IExpr:
  return IVal(-a)

def _sqr(a)->IExpr:
  return IVal(a*a)

def _sqrt(a)->IExpr:
  if a>=0:
    return IVal(int(sqrt(a)))
  else:
    return IError('Sqrt from negative')

def _succ(a)->IExpr:
  return IVal(a+1)

def _prec(a)->IExpr:
  return IVal(a-1)

def unpack(f):
  def _f(args):
    return f(**{an:a.val for an,a in args.items()})
  return _f

def mn(n:str)->MethodName:
  return MethodName(n)

lib:Lib = TMap({
  mn('add'): LibEntry(mn('add'), ['a','b'], unpack(_add)),
  mn('mul'): LibEntry(mn('mul'), ['a','b'], unpack(_mul)),
  mn('div'): LibEntry(mn('div'), ['a','b'], unpack(_div)),
  mn('neg'): LibEntry(mn('neg'), ['a'], unpack(_neg)),
  mn('sqr'): LibEntry(mn('sqr'), ['a'], unpack(_sqr)),
  mn('sqrt'): LibEntry(mn('sqrt'), ['a'], unpack(_sqrt)),
  mn('succ'): LibEntry(mn('succ'), ['a'], unpack(_succ)),
  mn('prec'): LibEntry(mn('prec'), ['a'], unpack(_prec)),
})

