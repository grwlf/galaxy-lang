from galang.interp import interp, Lib, LibRecord
from galang.edsl import let, call, num, wlet


def _add(a,b):
  return a+b
def _mul(a,b):
  return a*b
def _neg(a):
  return -a

testlib:Lib = {
  'add': LibRecord(_add, ['a','b']),
  'mul': LibRecord(_mul, ['a','b']),
  'neg': LibRecord(_neg, ['a'])
}

def test_let():
  e = let('x', num(33), lambda x: x)
  v = interp(e)
  assert v.val==33

def test_wlet():
  e = wlet(num(33), lambda x: x)
  v = interp(e)
  assert v.val==33

# def test_call():
#   e = let('x', num(33), lambda x: x)
#   v = interp(e)
#   assert v.val==33

