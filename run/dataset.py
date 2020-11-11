#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather
from galang.ser import json2t, t2json


from random import randint

def main():
  N = 3
  WLIB = mkwlib(lib_arith, 5)
  IMEM:IMem = mkmap({Ref(f"i{i}"): IVal(randint(0,100)) for i in range(N)})
  O:int = randint(0,100)
  acc:List[Expr] = []

  print(f"Inputs: {list(IMEM.values())}")
  print(f"Output: {O}")

  i = 0
  g = genexpr(WLIB, [IMEM])
  while len(acc)<1000:
    ref,mem,vals,w = next(g)
    ival = vals[0]
    assert isinstance(ival, IVal)
    if ival==IVal(O):
      expr = gather(ref,mem)
      acc.append(expr)
      print(f"Added {print_expr(expr)}, size is now {len(acc)}")
    i += 1
    if i%100 == 0:
      print(f".. i {i} W {w} LAST_REF {ref} LAST_VAL {ival} .. ")

if __name__ == "__main__":
  main()
