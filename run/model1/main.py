from typing import (List, Optional, Any, Dict, Iterable, Callable, Set,
                    Iterator, Tuple)

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import (MethodName, TMap, Dict, mkmap, Ref, Mem, Expr, Tuple,
                          NamedTuple, Example, Lib, mergemap)
from galang.serbin import fd2examples2, fd2examples
from galang.utils import freqs,print_expr
# from galang.ser import Example

from pylightnix import (Manager, Build, DRef, realize, instantiate,
                        store_initialize, mklens, mkconfig, mkdref,
                        build_wrapper, build_setoutpaths, promise, match_only,
                        mkdrv, linkrref, match_latest)

from pandas.core.groupby.generic import DataFrameGroupBy
from os import system, makedirs
from altair_saver import save as altair_save

from numpy import array
from numpy.random import choice, randint

from dataset1.stabilize import INDICES, load3

from torch import Tensor, LongTensor, cat
from torch.nn import Module, Linear, CrossEntropyLoss
from torch.optim import Adam
from torch.nn.functional import one_hot

import numpy as np
import torch

device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
assert str(device)=='cuda', f"Torch device is not 'cuda' but '{device}'"

class MLP(Module):
  def __init__(self):
    super(MLP, self).__init__()
    self.linear = Linear(28*28, 10)
  def forward(self, x):
    out = self.linear(x)
    return out

model = MLP().to(device)
optimizer = Adam(model.parameters())
criterion = CrossEntropyLoss()


def sample(N:int=5)->List[Example]:
  """ Samples `N` examples from the dataset """
  acc:List[Example]=[]
  while len(acc)<N:
    i=int(choice(INDICES, size=1)[0])
    n=0
    print('Loading section', i)
    try:
      with open(mklens(load3(i,False)).out_examples.syspath, 'rb') as ef:
        _,_skip=fd2examples2(ef)
        try:
          while True:
            _skip()
            n+=1
        except IndexError:
          pass
    except LookupError:
      print('Woops, no realization')
      continue
    x=randint(0,n-1)
    print('.. it contains', n, 'records, we take', x)
    with open(mklens(load3(i,False)).out_examples.syspath, 'rb') as ef:
      _next,_skip=fd2examples2(ef)
      for i in range(x-1):
        _skip()
      acc.append(_next())
  return acc

def i2b(i:int, sz:int=64)->List[int]:
  """ Returns `sz+1` bit string, upper bit represents the sign """
  # print(bin(i))
  return [0 if i>=0 else 1] + [int(n) for n in bin(abs(i))[2:].zfill(sz)]

def i2t(i:int)->LongTensor:
  """ Converts an integer into a one-hot encoded bit-vector """
  res=one_hot(LongTensor(i2b(i)), num_classes=2)
  assert res.shape==(64+1,2), f"Actually got a shape {res.shape}"
  return res

def features(e:Example, maxinp:int=2)->Tensor:
  inum=len(list(e.inp.values()))
  assert inum<=maxinp
  nums=[0]*(maxinp-inum) + [int(i.val) for i in e.inp.values()] + [int(e.out.val)]
  return cat([i2t(n) for n in nums], dim=0)

def labels(e:Example, l:Lib=lib_arith)->Tensor:
  s=mergemap(mkmap({mn:0 for mn in l.keys()}),freqs(e.expr),lambda x,y:x+y)
  f={mn:n/sum(s.values()) for mn,n in s.items()}
  # print({mn.val:i for mn,i in f.items()})
  return Tensor(list(f.values()))

