#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable, Set

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather

from pylightnix import realize, instantiate, store_initialize, Manager, mklens
from galang.stages.all import stage_inputs, stage_dataset1, stage_dataset2
from galang.serbin import fd2examples
from pandas import DataFrame
from os import system
from altair_saver import save as altair_save

import pandas as pd
import altair as alt

alt.data_transformers.disable_max_rows()

store_initialize()

def examples_refnames(fpath:str)->Set[Ref]:
  print(f"Reading {fpath}")
  acc:Set[Ref]=set()
  with open(fpath,'rb') as f:
    _next=fd2examples(f)
    try:
      i=0
      while True:
        example=_next()
        for r,v in example.inp.items():
          acc |= set({r})
        i+=1
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      pass
    return acc

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
    df=DataFrame(d)
    print(f"Number of examples: {i}")
    return df

def _axis(alt_fn, col, title):
  return alt_fn(col, axis=alt.Axis(title=title))

def vis_bars(df:DataFrame, plot_fpath:str=None)->None:
  fpath:str='_plot.png' if plot_fpath is None else plot_fpath

  Qi=0.0
  dfi=df[df['isin']==1].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  dfiq=dfi[dfi['cnt']>dfi['cnt'].quantile(Qi)]
  chi=alt.Chart(dfiq).mark_bar().encode(
    x=_axis(alt.X, 'data', f'Inputs above {Qi} quantile'),
    y=_axis(alt.Y, 'cnt', 'Count'))

  dfo=df[df['isin']==0].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  Qo=0.0
  dfoq=dfo[dfo['cnt']>dfo['cnt'].quantile(Qo)]
  cho=alt.Chart(dfoq).mark_bar().encode(
    x=_axis(alt.X, 'data', f'Outputs above {Qo} quantile'),
    y=_axis(alt.Y, 'cnt', 'Count'),
    color=alt.value('red'))

  print(f"Number of inputs: {len(df[df['isin']==1].index)}")
  print(f"Number of outputs: {len(df[df['isin']==0].index)}")
  print(f"Number of distinct inputs: {len(dfi.index)}")
  print(f"Number of distinct outputs: {len(dfo.index)}")
  altair_save(chi & cho,fpath)
  system(f"feh {fpath}")
  return

def load(ver:int=2, num_inputs:int=4, batch_size:int=5, **kwargs):
  def _stage(m:Manager):
    inp=stage_inputs(m, num_inputs=num_inputs, batch_size=batch_size)
    if ver==2:
      ds=stage_dataset2(m,inp,**kwargs)
    elif ver==1:
      ds=stage_dataset1(m,inp)
    else:
      raise ValueError(f'Invalid version {ver}')
    return ds
  rref=realize(instantiate(_stage))
  print(mklens(rref).syspath)
  print(examples_refnames(mklens(rref).out_examples.syspath))
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


