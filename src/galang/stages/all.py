from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import (MethodName, TMap, Dict, mkmap, Ref, Mem, Expr, IVal,
                          IExpr, IMem, Example)
from galang.utils import refs, print_expr, gather, gengather, extrefs, refs
from galang.serjson import jstr2expr, expr2jstr, imem2json, json2imem
from galang.serbin import (expr2bin, bin2expr, iexpr2bin, bin2iexpr, imem2bin,
                           bin2imem, BIN, examples2fd, fd2examples)

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
    out_examples = [promise, 'examples.bin']
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
    written_bytes = 0
    time_start = time()
    with open(mklens(b).out_examples.syspath,'wb') as f:
      _add=examples2fd(f)
      while time()<time_start+mklens(b).time2run_sec.val:
        r,mem,vals,w = next(g)
        ival = vals[0]
        assert isinstance(ival, IVal)
        expr = gather(r,mem)
        acc.append(expr)
        i += 1
        for j in range(len(IMEMs)):
          written_bytes+=_add(Example(IMEMs[j],expr,vals[j][r]))
        if i%300 == 0:
          print(f".. i {i} W {w} LAST_REF {r} WRBYTES {written_bytes}.. ")

  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))



def stage_dataset2(m:Manager, ref_inputs:DRef)->DRef:
  Wdef = 5
  lib_impl = lib_arith
  lib_methods = [mn.val for mn in lib_impl.keys()]
  time2run_sec = int(0.5*60)
  def _config():
    name = 'dataset2'
    nonlocal Wdef,lib_methods,time2run_sec
    num_inputs = mklens(ref_inputs).num_inputs.val
    batch_size = mklens(ref_inputs).batch_size.val
    inputs = mklens(ref_inputs).out_inputs.refpath
    out_examples = [promise, 'examples.bin']
    version = ['3']
    return locals()
  def _make(b:Build):
    build_setoutpaths(b, 1)
    WLIB = mkwlib(lib_impl, Wdef)
    IMEMs = [json2imem(j) for j in readjson(mklens(b).inputs.syspath)]
    print(f"Inputs: {IMEMs}")
    i = 0
    acc:List[Expr] = []
    g = genexpr(WLIB, IMEMs)
    written_bytes = 0
    time_start = time()
    with open(mklens(b).out_examples.syspath,'wb') as f:
      _add=examples2fd(f)
      while time()<time_start+mklens(b).time2run_sec.val:
        r,mem,imems,w = next(g)
        assert isinstance(imems[0][r], IVal), f"{imems[0][r]}"
        for expr in gengather(r,mem):
          acc.append(expr)
          i += 1
          for j in range(len(IMEMs)):
            inps = IMem({k:v for k,v in IMEMs[j].items() if k in extrefs(expr)})
            if len(refs(expr))>1:
              written_bytes+=_add(Example(inps,expr,imems[j][r]))
          if i%300 == 0:
            print(f".. i {i} W {w} LAST_REF {r} WRBYTES {written_bytes // (1024) }K .. ")

  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))

