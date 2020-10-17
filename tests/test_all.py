from galang.interp import interp, IVal
from galang.edsl import let, nnum, intrin, call
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, genexpr2, permute, WLib, mkwlib
from galang.types import MethodName

from hypothesis import given, assume, example, note, settings, event, HealthCheck
from hypothesis.strategies import (text, decimals, integers, characters,
                                   from_regex, dictionaries, one_of, lists,
                                   recursive, none, booleans, floats, composite,
                                   binary, just)

from ipdb import set_trace

def test_let()->None:
  e = let(nnum(33), lambda x: x)
  v = interp(e, lib_arith, {})
  assert isinstance(v, IVal)
  assert v.val==33

def test_wlet2()->None:
  e = let(nnum(33), lambda a:
      let(nnum(42), lambda b:
          intrin(MethodName("add"), {'a':a,'b':b})))

  v = interp(e, lib_arith, {})
  assert isinstance(v, IVal)
  assert v.val==33+42

def test_genexpr()->None:
  e = genexpr(3)
  v = interp(call(e, [nnum(x) for x in [1,2,3]]), lib_arith, {})
  assert isinstance(v, IVal), f"{v}"
  assert v.val==0

@given(ws=lists(integers(1,100),max_size=5),
       n=integers(0,4),
       W=integers(0,100))
def test_permute(ws,n,W)->None:
  ans = permute(ws, n, W)
  for a in ans:
    assert len(a)==n
    assert sum([ws[i] for i in a])==W

"""
def test_genexpr2()->None:
  wlib = mkwlib(lib_arith, 5)
  g=genexpr2(3,wlib)
  e1 = next(g)
  e2 = next(g)
"""



