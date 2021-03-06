from galang.interp import interp
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import (MethodName, TMap, Dict, mkmap, Ref, Mem, IVal, IExpr,
                          Expr, IMem, IVal, IAp, IError, ILam, Example,
                          mergemap, List)
from galang.utils import (refs_, extrefs, refs, decls, print_expr, gather,
                          gengather, freqs, check_expr)
from galang.serjson import (jstr2expr, expr2jstr, iexpr2jstr, jstr2iexpr, jstr2imem,
                        imem2jstr)
from galang.serbin import (expr2bin, bin2expr, iexpr2bin, bin2iexpr, bin2imem,
                           imem2bin, examples2fd, fd2examples, bin2ex, ex2bin)

from hypothesis import given, assume, example, note, settings, event, HealthCheck
from hypothesis.strategies import (text, decimals, integers, characters,
                                   from_regex, dictionaries, one_of, lists,
                                   recursive, none, booleans, floats, composite,
                                   binary, just)
from pytest import raises
from ipdb import set_trace
from multiprocessing import Pool



def test_mergemap()->None:
  def _mm(a:TMap[int,int], b:TMap[int,int], f)->TMap[int,int]:
    return mergemap(a,b,f)
  assert _mm(mkmap({1:1,2:2}),
                  mkmap({1:10,3:30}),
                  lambda a,b:a+b)==mkmap({1:11,2:2,3:30})
  assert _mm(mkmap({1:1,3:3}),mkmap({}), lambda a,b:int(a+b))==mkmap({1:1,3:3})
  assert _mm(mkmap({}),mkmap({1:1,3:3}), lambda a,b:int(a+b))==mkmap({1:1,3:3})

def test_freqs()->None:
  e = let(num(33), lambda a:
      let(num(42), lambda b:
          intrin(MethodName("add"), [('a',a),('b',b)])))
  assert freqs(e)[MethodName("add")]==1
  assert len(freqs(e))==1

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
  assert cache[x] is True

def _test_tmap_pickle(i:int)->TMap[int,str]:
  return TMap({i:str(i)})

def test_tmap_pickle()->None:
  accs=[]
  with Pool(2) as p:
    accs=p.map(_test_tmap_pickle, list(range(100)), chunksize=2)
  assert len(accs)==100
  assert all([accs[i][i]==str(i) for i in range(100)])

def test_refs()->None:
  e = let_('a', num(33), lambda a:
      let_('b', num(42), lambda b:
          intrin(MethodName("add"), [('a',a),('c',ref('c'))])))
  assert refs_(e)==set([Ref('a'),Ref('b'),Ref('c')])
  assert refs(e)==set([Ref('a'),Ref('c')])
  assert decls(e)==set([Ref('a'),Ref('b')])

EXPRS = [
  intrin(MethodName("add"), [('a',num(0)),('b',ref('1'))]),
  let_('a',num(33),lambda a: num(42)),
  ap(lam('a',lambda a: num(42)), num(33))
]

def test_print()->None:
  assert print_expr(intrin(MethodName("add"), [('a',num(0)),('b',ref('1'))])) == "add(a=0,b=1)"
  assert print_expr(let_('a',num(33),lambda a: num(42))) == "let a = 33 in 42"
  assert print_expr(ap(lam('a',lambda a: num(42)), num(33))) == "((a -> 42) 33)"

def test_gather()->None:
  mn = MethodName
  mem = Mem({
    Ref('a'): num(33),
    Ref('b'): intrin(mn('neg'),[('a',ref('i'))]),
    Ref('c'): intrin(mn('add'),[('a',ref('a')),('b',ref('b'))])
  })
  expr = gather(Ref('c'), mem)
  assert extrefs(expr)==set([Ref('i')])
  iexpr,_ = interp(expr, lib_arith, mkmap({Ref('i'):ival(32)}))
  assert iexpr == IVal(1)

def test_gengather()->None:
  mn = MethodName
  mem = Mem({
    Ref('a'): num(33),
    Ref('b'): intrin(mn('neg'),[('a',ref('i'))]),
    Ref('c'): intrin(mn('add'),[('a',ref('a')),('b',ref('b'))])
  })
  imem = IMem({
    Ref('i'): IVal(32),
    Ref('a'): IVal(33),
    Ref('b'): IVal(-32),
    Ref('c'): IVal(1)
  })
  exprs = gengather(Ref('c'), mem)
  for e in exprs:
    inps = IMem({k:v for k,v in imem.items() if k in extrefs(e)})
    iexpr,_ = interp(e, lib_arith, inps)
    print(print_expr(e), iexpr, inps.dict)
    assert iexpr == imem[Ref('c')]

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
    ref,mem,vals,exprw = next(g)
    expr = gather(ref,mem)
    iexpr,_ = interp(expr, lib_arith, imem)
    assert len(vals)==1
    assert iexpr==vals[0][ref]
    assert len(extrefs(expr))>0
    assert extrefs(expr).issubset(set([Ref('a'),Ref('b'),Ref('c')]))
    print(print_expr(expr), iexpr)

def test_serexpr():
  def _test(ie):
    assert ie == jstr2expr(expr2jstr(ie))
    assert ie == bin2expr(expr2bin(ie))
  _test(num(33))
  _test(ref('a'))
  _test(lam('b',lambda x:num(44)))
  _test(let_('a', num(33), lambda x: x))
  _test(ap(ref('a'),ref('b')))
  _test(intrin(MethodName('add'),[('a',num(1)),('b',ref('x'))]))

def test_serexpr2():
  wlib = mkwlib(lib_arith, 5)
  imem:IMem = mkmap({Ref('a'):ival(0),
                     Ref('b'):ival(1),
                     Ref('c'):ival(2)})
  g = genexpr(wlib, [imem])
  for i in range(1000):
    ref,mem,vals,w = next(g)
    expr1 = gather(ref,mem)
    expr2 = jstr2expr(expr2jstr(expr1))
    assert expr1==expr2
    expr2 = bin2expr(expr2bin(expr1))
    assert expr1==expr2

def test_seriexpr():
  def _test(ie):
    assert ie == bin2iexpr(iexpr2bin(ie))
    assert ie == jstr2iexpr(iexpr2jstr(ie))
  _test(IVal(33))
  _test(IVal("foo"))
  _test(IAp(ILam("pat", intrin(MethodName('neg'),[('a',ref('pat'))])), IVal(42)))
  _test(IError("the message"))

def test_serimem():
  def _test(ie):
    assert ie == bin2imem(imem2bin(ie))
    assert ie == jstr2imem(imem2jstr(ie))
  _test(mkmap({Ref('a'):ival(0),
               Ref('b'):ival(1),
               Ref('c'):ival(2)}))

def test_example():
  e=Example(inp=mkmap({Ref('a'):ival(0)}),
            expr=ap(ref('a'),ref('b')),
            out=IVal(33))

  with open('/tmp/binfile','wb') as f:
    add=examples2fd(f)
    add(e)
    add(e)

  with open('/tmp/binfile','rb') as f:
    _next=fd2examples(f)
    n=_next()
    assert n==e
    n=_next()
    assert n==e


def _test_example_pickle(i:int)->Example:
  e1=Example(
    inp=mkmap({}),
    expr=EXPRS[i % len(EXPRS)],
    out=IVal(i))
  e2=bin2ex(ex2bin(e1))
  check_expr(e2.expr)
  return e2

def test_example_pickle()->None:
  N=100
  acc=[]
  with Pool(2) as p:
    acc=p.map(_test_example_pickle, list(range(N)), chunksize=2)
  assert len(acc)==N
  for ex in acc:
    check_expr(ex.expr)

