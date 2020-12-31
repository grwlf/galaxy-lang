#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable, Set, Iterator

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
from pandas.core.groupby.generic import DataFrameGroupBy
from os import system
from altair_saver import save as altair_save
from numpy.random import choice

import pandas as pd
import altair as alt
import numpy as np

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
  """ Loads protobuf into a DataFrame """
  d:dict={'idx':[], 'data':[], 'isin':[]}
  print(f"Reading {fpath}")
  def _addval(v, isin:int, idx:int)->None:
    nonlocal d
    d['idx'].append(idx)
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
      idx=0
      while True:
        example=_next()
        for k,v in example.inp.items():
          _addval(v,isin=1,idx=idx)
        _addval(example.out,isin=0,idx=idx)
        idx+=1
    except KeyboardInterrupt:
      raise
    except Exception as e:
      print(e)
      pass
    df=DataFrame(d)
    print(f"Number of examples: {idx}")
    return df

def _axis(alt_fn, col, title):
  return alt_fn(col, axis=alt.Axis(title=title))

def vis_bars(df:DataFrame, plot_fpath:str=None,
             async_plot:Optional[bool]=True)->None:
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
  print(f"Saving {fpath}")
  altair_save(chi & cho,fpath)
  if async_plot is not None:
    system(f"feh {fpath} {'&' if async_plot else ''}")
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

def uniform_sampling_weights(dfg:List[DataFrame], maxwMul:float=1)->List[float]:
  maxw:float=max([len(g) for g in dfg])*maxwMul
  acc=[]
  for g in dfg:
    acc.append(maxw - len(g))
    # print(n, len(g), acc[-1])
  return np.array(acc) / sum(acc)

def filter_used(df:DataFrame, used_idx:Iterable[int])->DataFrame:
  return df[~df.idx.isin(used_idx)]


def group_outs(df):
  return [g for _,g in df[df['isin']==0].groupby(by=['data'], as_index=False)]


def iterate_uniform(df:DataFrame,
                    f_grp:Callable[[DataFrame],List[DataFrame]])->Iterator[Set[int]]:
  acc:Set[int]=set()  # Example idxes
  while True:
    gs = f_grp(df)
    if len(gs)==0:
      break
    print(len(gs))

    idxs=uniform_sampling_weights(gs, 1.1)

    acc_portion:Set[int]=set()
    for _ in range(100):
      gi:int=choice(list(range(len(gs))), 1, p=idxs)[0]
      idx=gs[gi].sample().idx.iloc[0]
      if idx not in acc:
        acc_portion.add(idx)

    df2 = filter_used(df, acc_portion)
    acc |= acc_portion
    yield acc
    df = df2

  return acc

def stabilize(df):
  for i,selected in enumerate(iterate_uniform(df, group_outs)):
    df2=df[df.idx.isin(selected)]
    vis_bars(df2, plot_fpath=f'_plot_{i:03d}.png', async_plot=None)


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


