#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable, Set, Iterator

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr, Tuple
from galang.utils import refs, print_expr, gather

from pylightnix import (Manager, Build, DRef, realize, instantiate,
                        store_initialize, Manager, mklens, mkconfig, mkdref,
                        build_wrapper, build_setoutpaths, promise, match_only,
                        mkdrv, linkrref, match_latest)
from galang.stages.all import stage_inputs, stage_dataset1, stage_dataset2
from galang.serbin import fd2examples
from pandas import DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from os import system
from altair_saver import save as altair_save
from numpy.random import choice
from scipy.stats import kstest
from collections import defaultdict
from copy import deepcopy

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
             async_plot:Optional[bool]=True,
             plot_title:Optional[str]=None)->None:
  fpath:str='_plot.png' if plot_fpath is None else plot_fpath

  Qi=0.0
  dfi=df[df['isin']==1].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  dfiq=dfi[dfi['cnt']>dfi['cnt'].quantile(Qi)]
  chi=alt.Chart(dfiq).mark_bar().encode(
    x=_axis(alt.X, 'data', f'Inputs above {Qi} quantile'),
    y=_axis(alt.Y, 'cnt', 'Count')).properties(
      title=f"Total {len(df[df['isin']==1].index)} entries")

  if plot_title is not None:
    chi=chi.properties(title=plot_title)

  dfo=df[df['isin']==0].groupby(by=['data'], as_index=False) \
                       .aggregate(cnt=pd.NamedAgg(column='isin', aggfunc='count'))
  Qo=0.0
  dfoq=dfo[dfo['cnt']>dfo['cnt'].quantile(Qo)]
  cho=alt.Chart(dfoq).mark_bar().encode(
    x=_axis(alt.X, 'data', f'Outputs above {Qo} quantile'),
    y=_axis(alt.Y, 'cnt', 'Count'),
    color=alt.value('red')).properties(
      title=f"Total {len(df[df['isin']==0].index)} entries")

  print(f"Number of inputs: {len(df[df['isin']==1].index)}")
  print(f"Number of outputs: {len(df[df['isin']==0].index)}")
  print(f"Number of distinct inputs: {len(dfi.index)}")
  print(f"Number of distinct outputs: {len(dfo.index)}")
  print(f"Saving {fpath}")
  altair_save((chi & cho),fpath)
  if async_plot is not None:
    system(f"feh {fpath} {'&' if async_plot else ''}")
  return


def stage_df(m:Manager, ref_data:DRef):
  def _config():
    nonlocal ref_data
    name=mklens(ref_data).name.val+'-df'
    examples=mklens(ref_data).out_examples.refpath
    out_df=[promise,'df.csv']
    return locals()
  def _make(b:Build):
    build_setoutpaths(b,1)
    df=examples_dataframe(mklens(b).examples.syspath)
    df.to_csv(mklens(b).out_df.syspath)
  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))

def stage_vis(m:Manager, ref_df:DRef):
  def _config():
    name=mklens(ref_df).name.val+'-vis'
    df=mklens(ref_df).out_df.refpath
    out_plot=[promise,'plot.png']
    title=mklens(ref_df).ref_data.name.val
    version=3
    return locals()
  def _make(b:Build):
    build_setoutpaths(b,1)
    df=pd.read_csv(mklens(b).df.syspath)
    vis_bars(df, plot_fpath=mklens(b).out_plot.syspath, async_plot=None,
             plot_title=mklens(b).title.val)
  return mkdrv(m, mkconfig(_config()), match_latest(), build_wrapper(_make))


def filter_used(df:DataFrame, used_idx:Iterable[int])->DataFrame:
  return df[~df.idx.isin(used_idx)]


#: Group identifier is a unique integer
GrpId=int
#: State contains the sizes of every group
GrpState=Dict[GrpId,int]
#: GrpFn splits a DataFrame into groups with uniq identifier
GrpFn=Callable[[DataFrame],Dict[GrpId,DataFrame]]

def group_outs(df:DataFrame)->Dict[GrpId,DataFrame]:
  """ Split DataFrame into non-intersecting groups, where each group has it's
  own unique identifier"""
  return {int(g['data'].mean()):g for _,g in
          df[df['isin']==0].groupby(by=['data'], as_index=False)}


def uniform_sampling_weights(gstate:GrpState,
                             gnew:Dict[GrpId,DataFrame],
                             maxwMul:float=1)->Tuple[Dict[GrpId,float],GrpState]:
  gstate2=deepcopy(gstate)
  for gid,g in gnew.items():
    gstate2[gid]+=len(g.index)
  maxw:float=max([gsize for _,gsize in gstate2.items()])*maxwMul
  acc={}
  for gid,g in gnew.items():
    acc[gid]=maxw-len(g.index)
  acc={gid:w/sum(acc.values()) for gid,w in acc.items()}
  return acc,gstate2

def iterate_uniform(df:DataFrame,
                    f_grp:GrpFn,
                    gstate:Optional[GrpState]=None
                    )->Iterator[Tuple[Set[int],GrpState]]:
  acc:Set[int]=set()  # Collected idxes of Examples
  gstate:GrpState=defaultdict(int) if gstate is None else gstate
  miss=0
  while True:
    gs:Dict[GrpId,DataFrame]=f_grp(df)
    if len(gs.keys())==0:
      break
    gsw,gstate2=uniform_sampling_weights(gstate, gs, 1.1)
    print('#groups-new', len(gs.keys()),
          '#groups-total', len(gstate2.keys()),
          '#entries-new', sum([len(g.index) for g in gs.values()]),
          '#group-misses', miss)
    acc_portion:Set[int]=set()
    gids:List[int]=choice(list(gsw.keys()), 100, p=list(gsw.values()))
    for gid in gids:
      assert gid in gs
      idx=gs[gid].sample().idx.iloc[0]
      if idx not in acc:
        acc_portion.add(idx)
      else:
        miss+=1
    df2 = filter_used(df, acc_portion)
    acc |= acc_portion
    yield acc,gstate2
    df=df2
    gstate=gstate2

  return acc

def stabilize(df):
  system("rm _plot*png")
  system("rm _stabilize_*png")
  acc:dict={'n':[],'data':[]}
  N=1000
  for i,(selected,gstate) in enumerate(iterate_uniform(df, group_outs)):
    df2=df[df.idx.isin(selected)]
    dfo=df2[df2['isin']==0]
    ksres=kstest(dfo['data'].sample(min(N,len(dfo.index))).to_numpy(),'uniform')
    print(ksres)
    acc['n'].append(len(dfo.index))
    acc['data'].append(ksres[0])
    vis_bars(df2, plot_fpath=f'_plot_{i:03d}.png', async_plot=None)
    altair_save(alt.Chart(DataFrame(acc)).mark_line().encode(
                          x='n', y='data').properties(),
                './stabilize.png')

def run(mode:int=2, interactive:bool=True):
  maxitems=5000
  Wdef=1
  gather_depth=None
  num_inputs=2
  if mode==1:
    batch_size=5
  elif mode==2:
    batch_size=1
  else:
    assert False, 'Invalid mode'

  def _stage(m:Manager):
    inp=stage_inputs(m, num_inputs=num_inputs, batch_size=batch_size)
    ds=stage_dataset2(m,inp,Wdef=Wdef, maxitems=maxitems,
                      gather_depth=gather_depth)
    df=stage_df(m, ds)
    dsvis=stage_vis(m,df)
    return dsvis

  rref=realize(instantiate(_stage), force_rebuild=interactive)
  linkrref(rref, '_results')
  if interactive:
    system(f"feh {mklens(rref).out_plot.syspath} &")
  return rref
  # df=examples_dataframe(mklens(rref).out_examples.syspath)
  # df2=df[~df['isin']].groupby(by=['data','isin'], as_index=False).count()
  # print(df2.head())
  # ch=alt.Chart(df[df['isin']==False]).mark_bar().encode(
  #     alt.X("data:Q", bin=alt.BinParams(maxbins=100)),
  #     y='count()')
  # altair_save(ch,'_plot.png')
  # system("feh _plot.png")
  # print('Done')

def load(what:int)->DataFrame:
  rref=run(what, interactive=False)
  df=pd.read_csv(mklens(rref).df.syspath)
  return df


def tryks():
  df=load(2)
  print(kstest(df[df['isin']==0]['data'].to_numpy(),'uniform'))

if __name__=='__main__':
  run()


