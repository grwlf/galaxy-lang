from galang.interp import interp, IVal
from galang.edsl import let, nnum, intrin
from galang.domain.arith import lib

def test_let()->None:
  e = let(nnum(33), lambda x: x)
  v = interp(e, lib, {})
  assert isinstance(v, IVal)
  assert v.val==33

def test_wlet2()->None:
  e = let(nnum(33), lambda a:
      let(nnum(42), lambda b:
          intrin("add", {'a':a,'b':b})))

  v = interp(e, lib, {})
  assert isinstance(v, IVal)
  assert v.val==33+42

# def test_call():
#   e = let('x', nnum(33), lambda x: x)
#   v = interp(e)
#   assert v.val==33
