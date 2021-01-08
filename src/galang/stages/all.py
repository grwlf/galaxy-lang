from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import (MethodName, TMap, Dict, mkmap, Ref, Mem, Expr, IVal,
                          IExpr, IMem, Example)
from galang.utils import (refs, print_expr, gather, gengather, extrefs, refs,
                          decls, depth)
from galang.serjson import jstr2expr, expr2jstr, imem2json, json2imem
from galang.serbin import (expr2bin, bin2expr, iexpr2bin, bin2iexpr, imem2bin,
                           bin2imem, BIN, examples2fd, fd2examples)

from pylightnix import (Build, Manager, DRef, Config, mkdrv, mkconfig,
                        match_only, build_wrapper, mklens, promise, writejson,
                        readjson, build_setoutpaths, realize, instantiate,
                        store_initialize, shell)
from sys import maxsize
from random import randint
from time import time
from psutil import virtual_memory
from copy import deepcopy

def _union(d1,d2):
  d=deepcopy(d1)
  d.update(d2)
  return d

def stage_inputs(m:Manager, num_inputs:int=4, batch_size:int=5, index:int=1)->DRef:
  range_min = -100
  range_max = 100
  def _config():
    name = 'dataset-inputs'
    nonlocal num_inputs, batch_size, range_min, range_max, index
    out_inputs = [promise, 'inputs.json']
    version = 4
    return locals()
  def _make(b:Build):
    build_setoutpaths(b, 1)
    builtin_inputs:dict={
                    # Ref("i0"):IVal(0),
                    # Ref("i1"):IVal(1)
                   }
    IMEMs:List[IMem] = [mkmap(_union(builtin_inputs,
                                     {Ref(f"i{i+len(builtin_inputs.keys())}"): IVal(randint(range_min,range_max))
                                       for i in range(num_inputs)}))
                                         for _ in range(batch_size)]
    writejson(mklens(b).out_inputs.syspath, [imem2json(M) for M in IMEMs])
  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))


def stage_dataset1(m:Manager, ref_inputs:DRef)->DRef:
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
        assert isinstance(ival[r], IVal)
        expr = gather(r,mem)
        acc.append(expr)
        i += 1
        for j in range(len(IMEMs)):
          written_bytes+=_add(Example(IMEMs[j],expr,vals[j][r]))
        if i%300 == 0:
          print(f".. i {i} W {w} LAST_REF {r} WRBYTES {written_bytes}.. ")

  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))



def stage_dataset2(m:Manager, ref_inputs:DRef,
                   gather_depth:Optional[int]=999,
                   Wdef:int=5,
                   maxtime_sec:Optional[int]=None,
                   maxitems:Optional[int]=None)->DRef:
  lib_impl = lib_arith
  lib_methods = [mn.val for mn in lib_impl.keys()]
  assert (maxtime_sec is not None) or (maxitems is not None), \
    "At least one stop criteria should be defined"
  time2run_sec:int = maxsize if maxtime_sec is None else maxtime_sec
  maxitems:int = maxsize if maxitems is None else maxitems
  def _config():
    nonlocal Wdef,lib_methods,time2run_sec,maxitems,gather_depth
    num_inputs = mklens(ref_inputs).num_inputs.val
    batch_size = mklens(ref_inputs).batch_size.val
    name=f'dataset2-ni{num_inputs}-bs{batch_size}-Wd{Wdef}-mi{maxitems}'
    inputs = mklens(ref_inputs).out_inputs.refpath
    out_examples = [promise, 'examples.bin']
    version = ['21']
    return locals()
  def _make(b:Build):
    build_setoutpaths(b, 1)
    WLIB = mkwlib(lib_impl, Wdef)
    IMEMs = [json2imem(j) for j in readjson(mklens(b).inputs.syspath)]
    print(f"Inputs: {IMEMs}")
    i = 0
    # acc:List[Expr] = []
    g = genexpr(WLIB, IMEMs)
    written_bytes = 0
    written_items = 0
    time_start = time()
    acci=set()
    hb=time()
    with open(mklens(b).out_examples.syspath,'wb') as f:
      _add=examples2fd(f)
      while time()<time_start+mklens(b).time2run_sec.val and \
            written_items<mklens(b).maxitems.val:
        # gt0=time()
        r,mem,imems,exprw = next(g)
        # gt1=time()
        # print('gen time', gt1-gt0)
        assert isinstance(imems[0][r], IVal), f"{imems[0][r]}"
        i += 1
        gi = 0
        gexpr = gengather(r,mem)
        # gg0=time()
        exprs=[]
        for expr in gexpr:
          exprs.append(expr)

        if gather_depth is not None:
          exprs=exprs[-gather_depth:]
        else:
          exprs=[exprs[randint(0,len(exprs)-1)]]

        for expr in exprs:
          er=extrefs(expr)
          ds=decls(expr)
          # acc.append(expr)
          for j in range(len(IMEMs)):
            if len(ds)>0:
              # print(gi, j, list(inps.keys()), print_expr(expr))
              inps = IMem({k:imems[j][k] for k in er})
              acci |= set(inps.values())
              written_bytes+=_add(Example(inps,expr,imems[j][r]))
              written_items+=1
              hb2=time()
              if written_items%100 == 0:
                print(f".. NW {written_items} W {exprw[r]} DEP {depth(expr)} "
                      f"LAST_REF {r} WRBYTES {written_bytes // (1024) }K "
                      f"INPSZ {len(acci)} TIME {hb2-hb} "
                      f"VM {virtual_memory().used // 1024 // 1024}M")
              hb=hb2
          gi+=1
        # gg1=time()
        # print('gather time', gg1-gg0)

  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))

