from galang.types import Expr
from galang.edsl import intrin, lam, let, ident, nnum
from galang.interp import Lib, IExpr
from typing import List, Dict, Optional, Iterable
from collections import OrderedDict

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


def genexpr2(nargs:int, lib:Lib,
             opweights:Dict[str,int])->List[Expr]:
  """ Generate lambda-expression with `nargs` arguments """

  # Output values accumulator
  vals:Dict[Expr,Optional[IExpr]] = {ident(f"arg-{i}"):None for i in range(nargs)}

  # TODO: Could we update this weights without evaluating expressions?
  valweights:Dict[Expr,int] = OrderedDict()

  # TODO: populate vals with deduced constants

  W = 0
  while True:
    W += 1
    for op in lib.values():
      n = len(op.args)
      w = opweights[op.name]
      nargs = len(op.args)
      argws = list(valweights.items())
      for indiset in permute([a[1] for a in argws], nargs, W-w):
        # op1 = intrin(op.name, {'a':None, 'b':None})
        args:List[Expr] = [argws[i][0] for i in indiset]



  assert False, "Not done yet"
  return None

