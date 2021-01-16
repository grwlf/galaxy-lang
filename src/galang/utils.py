from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName, mkmap, mergemap)
from galang.edsl import let_
from typing import List, Tuple, Dict, Union, Callable, Set, Optional, Iterator

from functools import lru_cache
from copy import deepcopy

@lru_cache(maxsize=128)
def refs_(e:Expr, declarations:bool=True, references:bool=True)->Set[Ref]:
  """ Collect `Ref`s used by `Expr`. Could find reference declarations only or
  references uses only. """
  d,r=declarations,references
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return set()
    elif isinstance(e.val, Ref):
      return set([e.val] if references else [])
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return refs_(e.body,d,r)
  elif isinstance(e, Let):
    return set([e.ref] if declarations else []) | refs_(e.expr,d,r) | refs_(e.body,d,r)
  elif isinstance(e, Ap):
    return refs_(e.func,d,r) | refs_(e.arg,d,r)
  elif isinstance(e, Intrin):
    acc:Set[Ref] = set()
    for a in e.args.values():
      acc |= refs_(a,d,r)
    return acc
  else:
    raise ValueError(f"Invalid expression {e}")

@lru_cache(maxsize=128)
def decls(e:Expr)->Set[Ref]:
  return refs_(e, declarations=True, references=False)

@lru_cache(maxsize=128)
def refs(e:Expr)->Set[Ref]:
  return refs_(e, declarations=False, references=True)

@lru_cache(maxsize=128)
def extrefs(e:Expr)->Set[Ref]:
  return refs(e)-decls(e)

def depth(e:Expr)->int:
  """ Prints the expression """
  if isinstance(e,Val):
    return 1
  elif isinstance(e, Ap):
    return max(depth(e.func),depth(e.arg))+1
  elif isinstance(e, Lam):
    return depth(e.body)+1
  elif isinstance(e, Let):
    return max(depth(e.expr),depth(e.body))+1
  elif isinstance(e, Intrin):
    return 1
  else:
    raise ValueError(f"Invalid expression '{e}'")

def print_expr(e:Expr)->str:
  """ Prints the expression """
  if isinstance(e,Val):
    if isinstance(e.val, Ref):
      return f"{e.val.name}"
    elif isinstance(e.val, Const):
      return f"{e.val.const}"
    else:
      raise ValueError(f"Invalid value-expr '{e}'")
  elif isinstance(e, Ap):
    return f"({print_expr(e.func)} {print_expr(e.arg)})"
  elif isinstance(e, Lam):
    return f"({e.name} -> {print_expr(e.body)})"
  elif isinstance(e, Let):
    return f"let {e.ref.name} = {print_expr(e.expr)} in {print_expr(e.body)}"
  elif isinstance(e, Intrin):
    return f"{e.name.val}({','.join([k+'='+print_expr(v) for k,v in sorted(e.args.items())])})"
  else:
    raise ValueError(f"Invalid expression '{e}'")

def freqs(e:Expr)->TMap[MethodName,int]:
  """ returns the intrinciq usage statistics """
  def mm(a,b):
    return mergemap(a,b,lambda x,y:x+y)
  if isinstance(e,Val):
    return mkmap({})
  elif isinstance(e, Ap):
    return mm(freqs(e.func), freqs(e.arg))
  elif isinstance(e, Lam):
    return freqs(e.body)
  elif isinstance(e, Let):
    return mm(freqs(e.expr), freqs(e.body))
  elif isinstance(e, Intrin):
    return mkmap({e.name:1})
  else:
    raise ValueError(f"Invalid expression '{e}'")


def gather(top:Ref, mem:Mem)->Expr:
  """ Re-constructs complext expression using top-level reference `top` and the
  map of references `mem`. Return the final expression. """
  mentioned:Set[Ref] = {top}
  acc:Optional[Expr] = None
  for ref,expr in reversed(list(mem.items())):
    if ref in mentioned:
      mentioned |= refs(expr)
      if acc is None:
        acc = expr
      else:
        acc2:Expr = acc
        acc = let_(ref.name, expr, lambda x: acc2)
  assert acc is not None
  return acc


def gengather(top:Ref, mem:Mem)->Iterator[Expr]:
  mentioned:Set[Ref] = {top}
  acc:Optional[Expr] = None
  for ref,expr in reversed(list(mem.items())):
    if ref in mentioned:
      mentioned |= refs(expr)
      if acc is None:
        acc = expr
      else:
        acc2:Expr = acc
        acc = let_(ref.name, expr, lambda x: acc2)
      yield acc



"""
def assemble(top:Ref, mem:Mem)->Expr:
  "" FIXME: has a bug, doesn't work ""
  visited:Set[Ref] = set()
  frontier:Set[Ref] = set([top])
  acc:Expr = mem[top]
  while frontier:
    i = frontier.pop()
    expr = mem[i]
    acc = let_(i.name, expr, lambda _: acc)
    visited.add(i)
    frontier |= refs(expr) - visited
  return acc
"""


"""
def dmerge(dicts:List[Dict[Any,Any]], ctr=int, agg=lambda a,b:a+b)->Dict[Any,Any]:
  acc:Dict[Any,Any] = defaultdict(ctr)
  for k,v in chain(*[d.items() for d in dicts]):
    acc[k] = agg(acc[k], v)
  return dict(acc)

def defs(e:Expr)->Dict[VRef,Expr]:
  if isinstance(e,Val):
    return {}
  elif isinstance(e,Let):
    return dmerge([{e.vref:e.expr},defs(e.body)], lambda: None, lambda a,b:b)
  elif isinstance(e,Intrin):
    return dmerge([defs(arg) for arg in e.args], lambda: None, lambda a,b:b)
  else:
    raise ValueError(f"Invalid expression {e}")

def nentries(e:Expr)->Dict[VRef,int]:
  if isinstance(e,Val):
    if isinstance(e.val, VRef):
      return {e.val:1}
    return {}
  elif isinstance(e,Let):
    return dmerge([nentries(e.expr),nentries(e.body)])
  elif isinstance(e,Intrin):
    return dmerge([nentries(arg) for arg in e.args])
  else:
    raise ValueError(f"Invalid expression {e}")

def subst(e:Expr, substs:Dict[VRef,Expr])->Expr:
  if isinstance(e,Val):
    if isinstance(e.val, VRef):
      if e.val in substs:
        return substs[e.val]
      else:
        return e
    else:
      return e
  elif isinstance(e,Let):
    if e.vref in substs:
      return subst(e.body, {vref:(subst(expr, {e.vref:substs[e.vref]})
                                  if vref!=e.vref else substs[e.vref])
                            for vref,expr in substs.items()})
    else:
      return Let(e.vref,
                 subst(e.expr, substs),
                 subst(e.body, substs))
  elif isinstance(e,Intrin):
    return Intrin(e.name, [subst(a,substs) for a in e.args])
  else:
    raise ValueError(f"Invalid expression {e}")

def simplify(e:Expr)->Expr:
  i = 0
  while True:
    l = defs(e)
    n = nentries(e)
    if all([x>1 for x in n.values()]):
      break
    substs = {vref:expr for vref,expr in l.items() if vref in n and n[vref]==1}
    if i>5:
      assert False
    # print(i)
    # print(print_expr(e))
    # print('defs:', l)
    # print('nums:', n)
    # print('substs:', substs)
    e = subst(e,substs)
    i+=1
  return e



def print_expr(e:Expr)->str:
  if isinstance(e,Val):
    if isinstance(e.val, VRef):
      return f"v{e.val.ident}"
    elif isinstance(e.val, ARef):
      return f"a{e.val.ident}"
    elif isinstance(e.val, Const):
      return f"{e.val.const}"
    else:
      raise ValueError(f"Invalid value-expr {e}")
  elif isinstance(e,Let):
    return f"let v{e.vref.ident} = {print_expr(e.expr)} in {print_expr(e.body)}"
  elif isinstance(e,Intrin):
    return f"{e.name.val}({','.join([print_expr(a) for a in e.args])})"
  else:
    raise ValueError(f"Invalid expression {e}")
"""

