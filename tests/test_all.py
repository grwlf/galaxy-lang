from galang.interp import interp, IVal
from galang.edsl import let, nnum, intrin, call
from galang.domain.arith import lib
from galang.gen import genexpr

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

def test_genexpr()->None:
  e = genexpr(3)
  v = interp(call(e, [nnum(x) for x in [1,2,3]]), lib, {})
  assert isinstance(v, IVal), f"{v}"
  assert v.val==0
