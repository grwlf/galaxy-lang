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


def examples_dataframe(fpath:str)->DataFrame:
  print(f"Reading {fpath}")
  d:dict={'data':[], 'isin':[]}
  def _addval(v, isin:int)->None:
    nonlocal d
    if isinstance(v,IVal) and \
       isinstance(v.val, int):
      d['data'].append(v.val)
      d['isin'].append(isin)
    else:
      d['data'].append(None)
      d['isin'].append(isin)
  with open(fpath,'rb') as f:
    _next=fd2examples(f)
    try:
      i=0
      while True:
        example=_next()
        for k,v in example.inp.items():
          _addval(v,isin=1)
        _addval(example.out,isin=0)
        i+=1
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      pass
    print(f"Number of examples: {i}")
    return DataFrame(d)

def _axis(alt_fn, col, title):
  return alt_fn(col, axis=alt.Axis(title=title))

def vis_bars(df:DataFrame, plot_fpath:str=None)->None:
  fpath:str='_plot.png' if plot_fpath is None else plot_fpath

  dfi=df[df['isin']==1].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  chi=alt.Chart(dfi).mark_bar().encode(
    x=_axis(alt.X, 'data', 'Inputs'),
    y=_axis(alt.Y, 'cnt', 'Count'))

  dfo=df[df['isin']==0].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  Q=0.7
  dfo=dfo[dfo['cnt']>dfo['cnt'].quantile(Q)]
  cho=alt.Chart(dfo).mark_bar().encode(
    x=_axis(alt.X, 'data', f'Outputs above {Q} quantile'),
    y=_axis(alt.Y, 'cnt', 'Count'),
    color=alt.value('red'))

  altair_save(chi & cho,fpath)
  system(f"feh {fpath}")
  return

def load():
  rref=build_dataset()
  print(mklens(rref).syspath)
  df=examples_dataframe(mklens(rref).out_examples.syspath)
  return df

def run():
  _=load()
  # df2=df[~df['isin']].groupby(by=['data','isin'], as_index=False).count()
  # print(df2.head())
  # ch=alt.Chart(df[df['isin']==False]).mark_bar().encode(
  #     alt.X("data:Q", bin=alt.BinParams(maxbins=100)),
  #     y='count()')
  # altair_save(ch,'_plot.png')
  # system("feh _plot.png")
  # print('Done')

if __name__=='__main__':
  run()


