from galang.interp import interp, IVal, IExpr, IMem, IVal, IAp, IError, ILam
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem
from galang.utils import refs, print_expr, gather
from galang.ser import json2t, t2json, iexpr2json, json2iexpr

from hypothesis import given, assume, example, note, settings, event, HealthCheck
from hypothesis.strategies import (text, decimals, integers, characters,
                                   from_regex, dictionaries, one_of, lists,
                                   recursive, none, booleans, floats, composite,
                                   binary, just)
from pytest import raises
from ipdb import set_trace

def test_eq()->None:
  assert let_('a', num(33), lambda x: x) == let_('a', num(33), lambda x: x)
  assert intrin(MethodName("add"), [('a',num(1)),('b',num(2))]) == \
         intrin(MethodName("add"), [('a',num(1)),('b',num(2))])
  assert ap(ref('a'),ref('b')) == ap(ref('a'),ref('b'))
  assert lam('a',lambda x:num(44)) == lam('a',lambda x:num(44))
  assert lam('a',lambda x:num(44)) != lam('a',lambda x:num(0))
  assert lam('a',lambda x:num(44)) != lam('b',lambda x:num(44))

def test_let1()->None:
  e = let(num(33), lambda x: x)
  v,_ = interp(e, lib_arith, mkmap())
  assert isinstance(v, IVal)
  assert v.val==33

def test_let2()->None:
  e = let(num(33), lambda a:
      let(num(42), lambda b:
          intrin(MethodName("add"), [('a',a),('b',b)])))

  v,_ = interp(e, lib_arith, mkmap())
  assert isinstance(v, IVal)
  assert v.val==33+42

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

def test_gather()->None:
  mn = MethodName
  mem = Mem({
    Ref('a'): num(33),
    Ref('b'): intrin(mn('neg'),[('a',ref('a'))]),
    Ref('c'): intrin(mn('add'),[('a',ref('a')),('b',ref('b'))])
  })
  expr = gather(Ref('c'), mem)
  iexpr,_ = interp(expr, lib_arith, mkmap())
  assert iexpr == IVal(0)

def ival(n:int)->IVal:
  r,_ = interp(num(n), lib_arith, mkmap())
  assert isinstance(r,IVal)
  return r

def test_genexpr()->None:
  wlib = mkwlib(lib_arith, 5)
  imem:IMem = mkmap({Ref('a'):ival(0),
                     Ref('b'):ival(1),
                     Ref('c'):ival(2)})
  g = genexpr(wlib, [imem])
  for i in range(1000):
    ref,mem,vals,w = next(g)
    expr = gather(ref,mem)
    iexpr,_ = interp(expr, lib_arith, imem)
    assert len(vals)==1
    assert iexpr==vals[0]
    print(print_expr(expr),iexpr)


def test_serexpr():
  wlib = mkwlib(lib_arith, 5)
  imem:IMem = mkmap({Ref('a'):ival(0),
                     Ref('b'):ival(1),
                     Ref('c'):ival(2)})
  g = genexpr(wlib, [imem])
  for i in range(1000):
    ref,mem,vals,w = next(g)
    expr1 = gather(ref,mem)
    expr2 = json2t(t2json(expr1))
    print(print_expr(expr1))
    print(print_expr(expr2))
    assert expr1==expr2

def test_seriexpr():
  def _test(ie):
    assert ie == json2iexpr(iexpr2json(ie))
  _test(IVal(33))
  _test(IVal("foo"))
  _test(IError("the message"))
  _test(IAp(ILam("pat", intrin(MethodName('neg'),[('a',ref('pat'))])), IVal(42)))


