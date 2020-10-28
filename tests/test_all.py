from galang.interp import interp, IVal
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, genexpr2, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref
from galang.utils import refs, print_expr

from hypothesis import given, assume, example, note, settings, event, HealthCheck
from hypothesis.strategies import (text, decimals, integers, characters,
                                   from_regex, dictionaries, one_of, lists,
                                   recursive, none, booleans, floats, composite,
                                   binary, just)

from ipdb import set_trace

def test_let()->None:
  e = let(num(33), lambda x: x)
  v,_ = interp(e, lib_arith, mkmap())
  assert isinstance(v, IVal)
  assert v.val==33

def test_wlet2()->None:
  e = let(num(33), lambda a:
      let(num(42), lambda b:
          intrin(MethodName("add"), [('a',a),('b',b)])))

  v,_ = interp(e, lib_arith, mkmap())
  assert isinstance(v, IVal)
  assert v.val==33+42

def test_genexpr()->None:
  e = genexpr(3)
  v,_ = interp(call(e, [num(x) for x in [1,2,3]]), lib_arith, mkmap())
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

def test_tmap()->None:
  x:TMap[int,str]=TMap({3:'3',4:'4'})
  def _f(a:str)->str:
    return a
  assert _f(x[3])=='3'
  cache:Dict[TMap[int,str],bool]={}
  cache[x] = True # Check hashability
  assert cache[x] == True

def test_refs()->None:
  e = let_('a', num(33), lambda a:
      let_('b', num(42), lambda b:
          intrin(MethodName("add"), [('a',a),('b',b)])))
  assert refs(e)==set([Ref('a'),Ref('b')])

def test_print()->None:
  assert print_expr(intrin(MethodName("add"), [('a',num(0)),('b',ref('1'))])) == "add(a=0,b=1)"
  assert print_expr(let_('a',num(33),lambda a: num(42))) == "let a = 33 in 42"
  assert print_expr(ap(lam('a',lambda a: num(42)), num(33))) == "((a -> 42) 33)"

"""
def test_genexpr2()->None:
  wlib = mkwlib(lib_arith, 5)
  g=genexpr2(3,wlib)
  e1 = next(g)
  e2 = next(g)
"""



