from galang.interp import Lib, LibEntry, IVal, MethodName, TMap


def _add(a,b):
  return a+b

def _mul(a,b):
  return a*b

def _div(a,b):
  try:
    return a/b
  except ZeroDivisionError:
    return float('inf')

def _neg(a):
  return -a

def unpack(f):
  def _f(args):
    return IVal(f(**{an:a.val for an,a in args.items()}))
  return _f

def mn(n:str)->MethodName:
  return MethodName(n)

lib:Lib = TMap({
  mn('add'): LibEntry(mn('add'), ['a','b'], unpack(_add)),
  mn('mul'): LibEntry(mn('mul'), ['a','b'], unpack(_mul)),
  mn('div'): LibEntry(mn('div'), ['a','b'], unpack(_div)),
  mn('neg'): LibEntry(mn('neg'), ['a'], unpack(_neg))
})
