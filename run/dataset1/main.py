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
from pandas import DataFrame
from os import system
from altair_saver import save as altair_save

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

store_initialize()


def build_dataset():
  def _stage(m:Manager):
    inp=stage_inputs(m)
    ds=stage_dataset(m,inp)
    return ds
  rref=realize(instantiate(_stage))
  return rref


def analyze_examples(fpath)->DataFrame:
  print(f"Reading {fpath}")
  d:dict={'data':[], 'isin':[]}
  def _addval(v, isin)->None:
    nonlocal d
    if isinstance(v,IVal) and \
       isinstance(v.val, int):
      d['data'].append(v.val)
      d['isin'].append(1 if isin else 0)
    else:
      d['data'].append(None)
      d['isin'].append(1 if isin else 0)
  with open(fpath,'rb') as f:
    _next=fd2examples(f)
    try:
      i=0
      while True:
        example=_next()
        for k,v in example.inp.items():
          _addval(v,True)
        _addval(example.out,False)
        i+=1
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      pass
    print(f"Number of examples: {i}")
    return DataFrame(d)

def run():
  rref=build_dataset()
  print(mklens(rref).syspath)
  df=analyze_examples(mklens(rref).out_examples.syspath)
  return df
  # df2=df[~df['isin']].groupby(by=['data','isin'], as_index=False).count()
  # print(df2.head())
  # ch=alt.Chart(df[df['isin']==False]).mark_bar().encode(
  #     alt.X("data:Q", bin=alt.BinParams(maxbins=100)),
  #     y='count()')
  # altair_save(ch,'plot.png')
  # system("feh plot.png")
  # print('Done')

if __name__=='__main__':
  run()


