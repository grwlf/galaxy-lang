from galang.types import Expr, MethodName, Ref, Mem, Val, TMap, Ref
from galang.edsl import intrin, lam, let, ref, num, mkname, let_
from galang.interp import Lib, IExpr, LibEntry, IMem, IVal, IError, interp
from galang.utils import refs
from typing import (List, Dict, Optional, Iterable, Tuple, Set, Iterator,
                    Callable)
from collections import OrderedDict

from ipdb import set_trace

def genexpr(nargs:int)->Expr:
  """ Generate lambda-expression with `nargs` arguments """

  def _genbody(avail:List[Expr]):
    return num(0)

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


def permute(weights:List[int], nargs:int, target_weight:int)->List[List[int]]:
  """ Return all combinations of indeces of `ws` of length `n` which sum up to
  `W` """
  ws = weights
  n = nargs
  W = target_weight
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

OpFilter=Dict[MethodName, Callable[[Expr,List[IExpr]],bool]]

def genexpr2(wlib:WLib,
             inputs:List[IMem]
             )->Iterator[Tuple[Ref,TMap[Ref,Expr],List[IExpr],int]]:
  """ Generate lambda-expression with `len(inputs)` arguments
  """
  # assert all([len(i)==nargs for i in inputs]), \
  #   f"All inputs should contain exactly `nargs` arguments ({nargs})." \
  #   f"The following inputs are invalid: {[i for i in inputs if len(i)!=nargs]}"

  # Accumulator of Output values
  # valcache:Dict[Expr,List[IMem]] = \
  #   {ref(f"arg-{n}"):[{ref(f"arg-{n}"):i[n]} for i in inputs] for n in range(nargs)}
  #
  # Should be:
  # valcache:Dict[Mem,List[IMem]] = ...
  #
  # Hint: Expressions depend on weights only via filters
  #
  # Algorithm inputs:
  # ----------------
  # wlib:WLib
  # inputs:List[List[IVal]]
  #
  # Algorithm state:
  # ---------------
  # exprw:Dict[Ref,int] = {}
  # exprcache:Dict[Ref,Intrin] = {}
  # valcache:Dict[Ref,List[IExpr]] = {}
  #
  # Algorithm outputs:
  # -----------------
  # Expressions accumulated from exprcache, its weight and List[IVal]
  #
  # TODO: Could we update this weights without evaluating expressions?

  # All inputs should provide the same input names
  assert all([i.keys()==inputs[0].keys() for i in inputs])
  nbatch = len(inputs)

  lib = {k:wl[0] for k,wl in wlib.items()}
  libws = {k:wl[1] for k,wl in wlib.items()}

  exprcache:Dict[Ref,Expr]={}
  exprw:Dict[Ref,int]={k:1 for k in inputs[0].keys()}
  valcache:Dict[Ref,List[IExpr]]={k:[i[k] for i in inputs] \
                                    for k in inputs[0].keys()}

  W = 0
  while True:
    W += 1
    for op in lib.values():
      n = len(op.argnames)
      w = libws[op.name]
      nargs = len(op.argnames)
      vws:List[Tuple[Ref,int]] = list(exprw.items())
      for valindices in permute(weights=[a[1] for a in vws], nargs=nargs, target_weight=W-w):
        argrefs:List[Ref] = [vws[i][0] for i in valindices]
        assert len(op.argnames)==len(argrefs)
        e2name = Ref(mkname('val'))
        e2expr = intrin(op.name, [(nm,Val(ai)) for nm,ai in zip(op.argnames, argrefs)])

        # TODO: Make this block customizable via callbacks
        acc:List[IExpr] = []
        for b in range(nbatch):
          e2val,_ = interp(e2expr, TMap(lib), TMap({nm:valcache[nm][b] for nm in argrefs}))
          acc.append(e2val)

        if any([isinstance(x,IError) for x in acc]):
          continue

        valcache[e2name] = acc
        exprcache[e2name] = e2expr
        exprw[e2name] = W
        yield (e2name,TMap(exprcache),acc,W)

