from galang.types import Expr, MethodName, Ident
from galang.edsl import intrin, lam, let, ident, nnum
from galang.interp import Lib, IExpr, LibEntry, Mem
from typing import List, Dict, Optional, Iterable, Tuple
from collections import OrderedDict

from ipdb import set_trace

def genexpr(nargs:int)->Expr:
  """ Generate lambda-expression with `nargs` arguments """

  def _genbody(avail:List[Expr]):
    return nnum(0)

  def _genlam(avail:List[Expr])->Expr:
    def _f(x):
      avail2 = avail + [x]
      return _genbody(avail2) if len(avail2)==nargs else _genlam(avail2)
    return lam(f'arg-{nargs}', _f)

  return _genlam([])


# def permute1(n:int, w:int)->List[int]:
#   """ Iterate over all permutations of `n` integer weights which sum up to `w`.
#   E.g.
#   for `w=1` => `[[0,1],[1,0]]`
#       `w=2` => `[[0,1,1],[1,0,1],[1,1,0],[0,0,2],[0,2,0],[2,0,0]]`
#       ...
#   """
#   assert w==0, f'Case of {w} is not implemented'
#   return []


def permute(ws:List[int], n:int, W:int)->List[List[int]]:
  """ Return all combinations of indeces of `ws` of length `n` which sum up to
  `W` """
  cache:Dict[int,List[List[int]]]={}
  def _go(W)->List[List[int]]:
    nonlocal cache
    if W<0:
      return []
    if W==0:
      return [[]]
    if W in cache:
      return cache[W]
    acc=[]
    for i in range(len(ws)):
      assert ws[i]>0, f"ws[{i}]({ws[i]}) <= 0"
      acc.extend([a+[i] for a in _go(W-ws[i]) if len(a)<=n-1])
    cache[W]=acc
    return acc
  return [a for a in _go(W) if len(a)==n]

WLib = Dict[MethodName, Tuple[LibEntry,int]]

def mkwlib(lib:Lib, default:int, weights:Optional[Dict[MethodName,int]]=None)->WLib:
  """ Define weights for the entries of a library """
  weights_ = weights if weights is not None else {}
  return {k:(e,weights_.get(k,default)) for k,e in lib.items()}


def genexpr2(nargs:int,
             wlib:WLib,
             inputs:List[List[IExpr]])->Iterable[Tuple[Expr,int]]:
  """ Generate lambda-expression with `nargs` arguments
  FIXME: broken!
  """
  assert all([len(i)==nargs for i in inputs]), \
    f"All inputs should contain exactly `nargs` arguments ({nargs})." \
    f"The following inputs are invalid: {[i for i in inputs if len(i)!=nargs]}"
  lib = {k:wl[0] for k,wl in wlib.items()}
  libws = {k:wl[1] for k,wl in wlib.items()}

  # Accumulator of Output values
  valcache:Dict[Expr,List[Mem]] = \
    {ident(f"arg-{n}"):[{Ident(f"arg-{n}"):i[n]} for i in inputs] for n in range(nargs)}

  # TODO: Could we update this weights without evaluating expressions?
  exprcache:Dict[Expr,int] = \
    OrderedDict({ident(f"arg-{i}"):1 for i in range(nargs)})

  W = 0
  while True:
    W += 1
    for op in lib.values():
      n = len(op.argnames)
      w = libws[op.name]
      nargs = len(op.argnames)
      vws = list(exprcache.items()) # Value Weights
      for valindices in permute([a[1] for a in vws], nargs, W-w):
        args:List[Expr] = [vws[i][0] for i in valindices]
        assert len(op.argnames)==len(args)
        # set_trace()
        e = intrin(op.name, {a:v for a,v in zip(op.argnames, args)})
        # valcache[e] = []
        exprcache[e] = W
        yield (e,W)


