from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather
from galang.serjson import jstr2expr, expr2jstr, imem2json, json2imem

from pylightnix import (Build, Manager, DRef, Config, mkdrv, mkconfig,
                        match_only, build_wrapper, mklens, promise, writejson,
                        readjson, build_setoutpaths, realize, instantiate,
                        store_initialize, shell)
from random import randint
from time import time


def stage_inputs(m:Manager)->DRef:
  num_inputs = 4
  batch_size = 5
  range_min= 0
  range_max = 100
  def _config():
    name = 'dataset-inputs'
    nonlocal num_inputs, batch_size, range_min, range_max
    out_inputs = [promise, 'inputs.json']
    return locals()
  def _make(b:Build):
    build_setoutpaths(b, 1)
    IMEMs:List[IMem] = [mkmap({Ref(f"i{i}"): IVal(randint(range_min,range_max))
                         for i in range(num_inputs)})
                           for _ in range(batch_size)]
    writejson(mklens(b).out_inputs.syspath, [imem2json(M) for M in IMEMs])
  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))


def stage_dataset(m:Manager, ref_inputs:DRef)->DRef:
  Wdef = 5
  lib_impl = lib_arith
  lib_methods = [mn.val for mn in lib_impl.keys()]
  time2run_sec = int(0.5*60)
  def _config():
    nonlocal Wdef,lib_methods,time2run_sec
    num_inputs = mklens(ref_inputs).num_inputs.val
    batch_size = mklens(ref_inputs).batch_size.val
    inputs = mklens(ref_inputs).out_inputs.refpath
    # out_outputs = [promise, 'outputs.json']
    out_expressions = [promise, 'exprs.jsons']
    version = ['0']
    return locals()
  def _make(b:Build):
    build_setoutpaths(b, 1)
    WLIB = mkwlib(lib_impl, Wdef)
    IMEMs = [json2imem(j) for j in readjson(mklens(b).inputs.syspath)]
    print(f"Inputs: {IMEMs}")
    i = 0
    acc:List[Expr] = []
    g = genexpr(WLIB, IMEMs)
    time_start = time()
    with open(mklens(b).out_expressions.syspath,'w') as f:
      while time()<time_start+mklens(b).time2run_sec.val:
        ref,mem,vals,w = next(g)
        ival = vals[0]
        assert isinstance(ival, IVal)
        expr = gather(ref,mem)
        acc.append(expr)
        i += 1
        if i%1000 == 0:
          print(f".. i {i} W {w} LAST_REF {ref} LAST_VAL {ival} .. ")
          f.write('\n'.join([expr2jstr(e) for e in acc])+'\n')
  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))



