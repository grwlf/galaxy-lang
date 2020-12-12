from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather
from galang.ser import json2expr, expr2json, exprs2json, imem2json

from random import randint

from pylightnix import (Build, Manager, DRef, Config, mkdrv, mkconfig,
                        match_only, build_wrapper, mklens, promise, writejson,
                        build_setoutpaths)


def stage_dataset(m:Manager)->DRef:
  N = 3
  Wdef = 5
  MaxAcc = 100
  lib_impl = lib_arith
  lib_methods = [mn.val for mn in lib_impl.keys()]
  def _config():
    nonlocal N,Wdef,MaxAcc,lib_methods
    revisions = ['0']
    inputs = [promise, 'inputs.json']
    outputs = [promise, 'outputs.json']
    out_expressions = [promise, 'exprs.json']
    return mkconfig(locals())

  def _make(b:Build):
    build_setoutpaths(b, 1)

    WLIB = mkwlib(lib_impl, Wdef)
    IMEM:IMem = mkmap({Ref(f"i{i}"): IVal(randint(0,100)) for i in range(N)})

    O:int = randint(0,100)
    acc:List[Expr] = []

    print(f"Inputs: {list(IMEM.values())}")
    print(f"Output: {O}")

    writejson(mklens(b).inputs.syspath, imem2json(IMEM))
    writejson(mklens(b).outputs.syspath, O)

    i = 0
    g = genexpr(WLIB, [IMEM])
    while len(acc)<MaxAcc:
      ref,mem,vals,w = next(g)
      ival = vals[0]
      assert isinstance(ival, IVal)
      if ival==IVal(O):
        expr = gather(ref,mem)
        acc.append(expr)
        writejson(mklens(b).out_expressions.syspath, exprs2json(acc))
        print(f"Added {print_expr(expr)}, size is now {len(acc)}")
      i += 1
      if i%100 == 0:
        print(f".. i {i} W {w} LAST_REF {ref} LAST_VAL {ival} .. ")
    pass

  return mkdrv(m, _config(), match_only(), build_wrapper(_make))



