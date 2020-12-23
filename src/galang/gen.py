from galang.types import (Lib, IExpr, LibEntry, IMem, IVal, IError, Expr,
                          MethodName, Ref, Mem, Val, TMap, Ref)
from galang.edsl import intrin, lam, let, ref, num, mkname, let_
from galang.interp import interp
from typing import (List, Dict, Optional, Iterable, Tuple, Set, Iterator,
                    Callable)
from collections import OrderedDict

from ipdb import set_trace


def permute(weights:List[int], nargs:int, target_weight:int)->List[List[int]]:
  """ Return all combinations of indeces of `ws` of length `n` which sum up to

  Iterate over all permutations of `weights` sum up to `target_weight`.
  E.g.
  for `w=1` => `[[0,1],[1,0]]`
      `w=2` => `[[0,1,1],[1,0,1],[1,1,0],[0,0,2],[0,2,0],[2,0,0]]`
      ...
 """
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

def genexpr(wlib:WLib,
            inputs:List[IMem]
            )->Iterator[Tuple[Ref,TMap[Ref,Expr],List[IMem],int]]:
  """ Iterate over space of lambda-expressions with `len(inputs[0])` input
  arguments. For every expression visited, provide results of
  it's evaluation on every input of the `intputs` list.

  Arguments:
  * `wlib`: Weighted library of primitive operations. See also `mkwlib`.
  * `inputs`: Collection of the inputs on which to grow the expression. All
    inputs in list should be of the same size and use same names.

  Yields a tuple of:
  * Top-level reference `Ref`
  * Map of `Ref -> Intrin`. Where `Intrin`s may contain more refs from the same
    map.
  * List of output expressions. Size of this list is equal to the size of
    list of `inputs`.
  * Current weight of the expression.
  """

  # All inputs should provide the same input names
  assert all([i.keys()==inputs[0].keys() for i in inputs])
  nbatch = len(inputs)

  lib = {k:wl[0] for k,wl in wlib.items()}
  libws = {k:wl[1] for k,wl in wlib.items()}

  exprcache:Dict[Ref,Expr]={}
  exprw:Dict[Ref,int]={k:1 for k in inputs[0].keys()}
  valcache:List[Dict[Ref,IExpr]]=[OrderedDict(i.dict) for i in inputs]

  W = 0
  while True:
    W += 1
    for op in lib.values():
      w = libws[op.name]
      nargs = len(op.argnames)
      vws:List[Tuple[Ref,int]] = list(exprw.items())
      for valindices in permute(weights=[a[1] for a in vws],
                                nargs=nargs, target_weight=W-w):
        argrefs:List[Ref] = [vws[i][0] for i in valindices]
        assert len(op.argnames)==len(argrefs)
        e2name = Ref(mkname('val'))
        e2expr = intrin(op.name, [(nm,Val(ai))
                                  for nm,ai in zip(op.argnames, argrefs)])

        # TODO: Make this block customizable via callbacks
        acc:List[IExpr] = []
        for b in range(nbatch):
          e2val,_ = interp(e2expr, TMap(lib), TMap(valcache[b]))
          acc.append(e2val)

        if any([isinstance(x,IError) for x in acc]):
          continue
        if isinstance(e2val,IVal) and isinstance(e2val.val, int):
          if any([abs(e2val.val)>10000 or abs(e2val.val)<-10000 for x in acc]):
            continue

        for b in range(nbatch):
          valcache[b][e2name] = acc[b]

        exprcache[e2name] = e2expr
        exprw[e2name] = W
        yield (e2name,TMap(exprcache),[TMap(fd) for fd in valcache],W)

