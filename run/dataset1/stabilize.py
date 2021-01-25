#!/usr/bin/env python3

from multiprocessing import Pool
from typing import List, Optional, Any, Dict, Iterable, Callable, Set, Iterator

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import (MethodName, TMap, Dict, mkmap, Ref, Mem, Expr, Tuple,
                          NamedTuple)
from galang.utils import refs, print_expr, gather

from pylightnix import (Manager, Build, DRef, realize, instantiate,
                        store_initialize, Manager, mklens, mkconfig, mkdref,
                        build_wrapper, build_setoutpaths, promise, match_only,
                        mkdrv, linkrref, match_latest, redefine)
from galang.stages.all import stage_inputs, stage_dataset1, stage_dataset2
from galang.serbin import fd2examples, examples2fd
from pandas import DataFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from os import system, makedirs
from altair_saver import save as altair_save
from numpy.random import choice
from scipy.stats import kstest
from collections import defaultdict
from copy import deepcopy
from os.path import join, isfile


import pandas as pd
import altair as alt
import numpy as np

alt.data_transformers.disable_max_rows()

store_initialize()

def examples2dataframe(fpath:str)->DataFrame:
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
    df=examples2dataframe(mklens(b).examples.syspath)
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


#: Group identifier is a unique integer
GrpId=int
#: State contains the sizes of every group
GrpState=Dict[GrpId,int]
#: GrpFn splits a DataFrame into groups with uniq identifier
GrpFn=Callable[[DataFrame],Dict[GrpId,DataFrame]]

def group_ins(df:DataFrame)->Dict[GrpId,DataFrame]:
  """ Split DataFrame into non-intersecting groups, where each group has it's
  own unique identifier"""
  return {int(g['data'].mean()):g for _,g in
          df[df['isin']==1].groupby(by=['data'], as_index=False)}

def group_outs(df:DataFrame)->Dict[GrpId,DataFrame]:
  """ Split DataFrame into non-intersecting groups, where each group has it's
  own unique identifier"""
  return {int(g['data'].mean()):g for _,g in
          df[df['isin']==0].groupby(by=['data'], as_index=False)}


def uniform_sampling_weights(gstate:GrpState,
                             gnew:Dict[GrpId,DataFrame],
                             maxwMul:float=1)->Dict[GrpId,float]:
  gstate2=deepcopy(gstate)
  for gid,g in gnew.items():
    gstate2[gid]+=len(g.index)
  maxw:float=max([gsize for _,gsize in gstate2.items()])*maxwMul
  acc={}
  for gid,g in gnew.items():
    acc[gid]=maxw-len(g.index)
  acc={gid:w/sum(acc.values()) for gid,w in acc.items()}
  return acc

def promote_uniform(gs:Dict[GrpId,DataFrame],
                    gstate:GrpState,
                    npoints:int=100)-> Set[int]:
  miss=0
  acc:Set[int]=set()  # Collected idxes of Examples
  if len(gs.keys())==0:
    return set()
  gsw=uniform_sampling_weights(gstate, gs, 1.1)
  print('#groups-new', len(gs.keys()),
        '#entries-new', sum([len(g.index) for g in gs.values()]),
        '#group-misses', miss)
  gids:List[int]=choice(list(gsw.keys()), npoints, p=list(gsw.values()))
  for gid in gids:
    assert gid in gs
    idx=gs[gid].sample().idx.iloc[0]
    if idx not in acc:
      acc.add(idx)
    else:
      miss+=1
  return acc

  # df2=remove_used(df, acc_portion)

class StabState:
  def __init__(self):
    self.inp:GrpState=defaultdict(int)
    self.out:GrpState=defaultdict(int)

def stabilize(df0, sstate:StabState=StabState(),
              min_allow_size:int=5000,
              npoints:int=100,
              path_barplot=lambda i:f'_plot_{i:03d}.png',
              path_traceplot:str='./_stabilize.png')->Set[int]:
  """
  FIXME: fix the state, introduce GrpState re-calculation based on currently
  allowed examples.
  """
  # system("rm _plot*png")
  # system("rm _stabilize*png")
  acc:dict={'n':[],'stati':[], 'stato':[]}
  N=1000 # How many data to track for KS-metric

  i=0
  allowed:Set[int]=set()
  df=df0

  def _remove_used(used_idx:Iterable[int]):
    nonlocal df, sstate, allowed
    for d in df[df.idx.isin(used_idx) & df['isin']==1]['data']:
      sstate.inp[d]+=1
    for d in df[df.idx.isin(used_idx) & df['isin']==0]['data']:
      sstate.out[d]+=1
    df=df[~df.idx.isin(used_idx)]
    allowed|=set(used_idx)

  while True:
    print(f"i={i}")

    if len(allowed)>=min_allow_size:
      print(f'Got enough examples: collected {len(allowed)}>={min_allow_size}')
      break

    used_o=promote_uniform(group_outs(df), sstate.out, npoints)
    if len(used_o)==0:
      print('No more data to pass through the filter')
      break
    _remove_used(used_o)


    # used_i=promote_uniform(group_ins(df), sstate.inp)
    # if len(used_i)==0:
    #   print('No difference in inputs')
    #   break
    # _remove_used(used_i)

    acc['n'].append(len(allowed))
    dfu=df0[df0.idx.isin(allowed)]
    dfo=dfu[dfu['isin']==0]
    # print(dfo)
    ksres=kstest(dfo['data'].sample(min(N,len(dfo.index))).to_numpy(),'uniform')
    acc['stato'].append(ksres[0])
    dfi=dfu[dfu['isin']==1]
    ksres=kstest(dfi['data'].sample(min(N,len(dfi.index))).to_numpy(),'uniform')
    acc['stati'].append(ksres[0])
    vis_bars(dfu, plot_fpath=path_barplot(i), async_plot=None)
    altair_save(alt.Chart(DataFrame(acc)).mark_line(color='red').encode(x='n', y='stato')+
                alt.Chart(DataFrame(acc)).mark_line(color='blue').encode(x='n', y='stati'),
                path_traceplot)
    i+=1
  return allowed

def run_dataset2(what:int=2, maxitems:int=5000, index:int=1, interactive:bool=True):
  Wdef=1
  gather_depth=None
  num_inputs=2
  if what==1:
    batch_size=5
  elif what==2:
    batch_size=1
  else:
    assert False, 'Invalid `what` argument'

  def _stage(m:Manager):
    inp=stage_inputs(m, num_inputs=num_inputs, batch_size=batch_size,
                     index=index)
    ds=stage_dataset2(m, inp, Wdef=Wdef, maxitems=maxitems,
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

def load2(what:int)->DataFrame:
  rref=run_dataset2(what, interactive=False)
  df=pd.read_csv(mklens(rref).df.syspath)
  return df


def tryks():
  df=load2(2)
  print(kstest(df[df['isin']==0]['data'].to_numpy(),'uniform'))


def stage_datasetS(m:Manager, index:int=0, Nvalid:int=5000, npoints:int=100)->DRef:
  """ Creates stabilized dataset """
  def _config():
    name='dataset3'
    nonlocal index, npoints
    N=int(5*Nvalid/3)
    min_allow_size=Nvalid
    out_examples=[promise,'examples.bin']
    out_barplots=[promise,'barplots']
    out_traceplot=[promise,'traceplot.png']
    out_inputs = [promise, 'inputs.json']
    version = 2
    return locals()
  def _make(b:Build):
    build_setoutpaths(b,1)
    rref=run_dataset2(what=2, maxitems=mklens(b).N.val, index=index, interactive=False)
    assert isfile(mklens(rref).ref_df.examples.syspath)
    system(f"cp {mklens(rref).ref_df.ref_data.inputs.syspath} {mklens(b).out_inputs.syspath}")
    df=pd.read_csv(mklens(rref).df.syspath)
    makedirs(mklens(b).out_barplots.syspath)
    allowed=stabilize(df,
                      npoints=mklens(b).npoints.val,
                      path_barplot=lambda i: join(mklens(b).out_barplots.syspath,
                                                  f'_plot_{i:03d}.png'),
                      path_traceplot=mklens(b).out_traceplot.syspath,
                      min_allow_size=mklens(b).min_allow_size.val)
    with open(mklens(rref).ref_df.examples.syspath,'rb') as f:
      with open(mklens(b).out_examples.syspath,'wb') as f_o:
        _read=fd2examples(f)
        _write=examples2fd(f_o)
        try:
          idx=0
          while True:
            example=_read()
            if idx in allowed:
              _write(example)
            idx+=1
        except KeyboardInterrupt:
          raise
        except Exception as e:
          print(e)
          pass
  return mkdrv(m, mkconfig(_config()), match_only(), build_wrapper(_make))

Nall=1000000
N1=15000
INDICES=list(range(Nall//N1))

def load3(index, allow_realize:bool=True):
  """ Loads the stabilized dataset. Raises LookupError if realization is
  forbidden and the data are absent. """
  if allow_realize:
    stage=stage_datasetS
  else:
    def _err(*args, **kwargs):
      raise LookupError("Attempting to realize dataset section with index {index}")
    stage=redefine(stage_datasetS, new_realizer=_err)
  return realize(instantiate(stage, index=index, Nvalid=N1, npoints=2000))

def myprocess(index):
  rref=load3(index)
  linkrref(rref, join('.','_results','dataset3-1K',f"{index:04d}"))
  return rref

def run(nproc:int):
  with Pool(nproc) as p:
    p.map(myprocess, INDICES)

if __name__=='__main__':
  run(10)



