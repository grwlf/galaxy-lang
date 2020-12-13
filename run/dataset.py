#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather

from pylightnix import realize, instantiate, store_initialize, Manager, mklens
from galang.stages.all import stage_inputs, stage_dataset
from galang.serbin import fd2examples


store_initialize()


def run():
  def _stage(m:Manager):
    inp=stage_inputs(m)
    ds=stage_dataset(m,inp)
    return ds
  rref=realize(instantiate(_stage))
  return rref


def check_examples(fpath):
  print(f"Reading {fpath}")
  with open(fpath,'rb') as f:
    _next=fd2examples(f)
    try:
      i=0
      while True:
        ex=_next()
        i+=1
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      pass
    print(f"Number of examples: {i}")


if __name__=='__main__':
  rref=run()
  print(mklens(rref).syspath)
  check_examples(mklens(rref).out_examples.syspath)
