from galang.interp import Lib, LibEntry, IVal


def _add(a,b):
  return a+b

def _mul(a,b):
  return a*b

def _div(a,b):
  return a//b

def _neg(a):
  return -a

def unpack(f):
  def _f(args):
    return IVal(f(**{an:a.val for an,a in args.items()}))
  return _f

lib:Lib = {
  'add': LibEntry('add', ['a','b'], unpack(_add)),
  'mul': LibEntry('mul', ['a','b'], unpack(_mul)),
  'div': LibEntry('div', ['a','b'], unpack(_div)),
  'neg': LibEntry('neg', ['a'], unpack(_neg))
}
