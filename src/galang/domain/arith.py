from sys import maxsize
from galang.interp import Lib, LibEntry, IVal, MethodName, TMap, IError, IExpr


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
  mn('neg'): LibEntry(mn('neg'), ['a'], unpack(_neg))
})
