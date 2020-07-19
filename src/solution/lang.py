from typing import ( Union, List, Optional, Any, Callable, Dict, Tuple )
from dataclasses import dataclass
from collections import OrderedDict
from ipdb import set_trace
from contextlib import contextmanager

#  ____
# |  _ \ __ _ _ __ ___  ___
# | |_) / _` | '__/ __|/ _ \
# |  __/ (_| | |  \__ \  __/
# |_|   \__,_|_|  |___/\___|


TERMS:Dict[str,'Term']={}
collect_ops:bool=True

@dataclass(frozen=True, eq=True)
class Term:
  name:str
  nargs:int

  def __post_init__(self):
    if collect_ops:
      global TERMS
      assert self.name not in TERMS
      TERMS[self.name]=self

T=Term('t',0)
F=Term('f',0)
nil=Term('nil',0)
inc=Term('inc',1)
dec=Term('dec',1)
add=Term('add',2)
mul=Term('mul',2)
div=Term('div',2)
eq=Term('eq',2)
lt=Term('lt',2)
mod=Term('mod',1) # has a list version
dem=Term('dem',1)
send=Term('send',1)
neg=Term('neg',1)
ap=Term('ap',2)
S=Term('s',3)
C=Term('c',3)
B=Term('b',3)
pwr2=Term('pwr2',1)
I=Term('i',1)
cons=Term('cons',3)
vec=Term('vec',2)
car=Term('car',1)
cdr=Term('cdr',1)
isnil=Term('isnil',1)
draw=Term('draw',1) # [x,y]->img
checkerboard=Term('checkerboard',2)
multipledraw=Term('multipledraw',1) # [x]->img???
if0=Term('if0',3)
collect_ops=False

def isterm(s:str)->bool:
  return s in set(TERMS.keys())

def mkterm(s:str)->Term:
  return TERMS[s]

from enum import Enum
class TType(Enum):
  """ Token types"""
  Int=0
  List=2
  Term=3
  Ref=4

# @dataclass
# class Picture:
#   data:List[Tuple[int,int]]

@dataclass(frozen=True)
class Ref:
  to:str

def isref(s:str)->bool:
  return len(s)>0 and (s[0].isalpha() or s[0]==':') and (s not in TERMS)

def mkref(s:str)->Ref:
  assert isref(s), f"{s}"
  return Ref(s)

REFIDX:int=0

def newref(suffix:str='x')->Ref:
  global REFIDX
  ref=mkref(f"{suffix}{REFIDX}"); REFIDX+=1
  return ref


@dataclass
class Token:
  typ:TType
  val:Union[int,list,Term,Ref]

def isint(w:str)->bool:
  try:
    return str(int(w))==w
  except ValueError:
    return False

Word=str
Line=List[Word]

def assert_isline(s:Any)->None:
  assert isinstance(s,list)
  if len(s)>0:
    assert isinstance(s[0],str)

# @dataclass
# class Assign:
#   name:Ref
#   expr:List[Token]

def parse_expr(line:str)->List[Token]:
  acc=[]
  for w in line.split():
    if isint(w):
      acc.append(Token(TType.Int, int(w)))
    elif isref(w):
      acc.append(Token(TType.Ref, mkref(w)))
    elif isterm(w):
      acc.append(Token(TType.Term, mkterm(w)))
    else:
      raise ValueError(f'Unknown expr token "{w}"')
  return acc

def parse_assign(ws:str)->Tuple[Ref,List[Token]]:
  parts=ws.split('=')
  assert len(parts)==2, f"{ws}"
  patterns=parts[0].split()
  assert len(patterns)==1
  ref=mkref(patterns[0])
  toks=parse_expr(parts[1])
  return ref,toks

@dataclass
class Program:
  body:Dict[Ref,List[Token]]


def parse_program(src:str)->Program:
  acc=OrderedDict()
  lines=src.split('\n')
  for l in lines:
    if len(l.strip())==0 or l.strip()[0]=='#':
      continue
    ref,toks=parse_assign(l)
    acc[ref]=toks
  return Program(acc)




#  ___       _                           _
# |_ _|_ __ | |_ ___ _ __ _ __  _ __ ___| |_
#  | || '_ \| __/ _ \ '__| '_ \| '__/ _ \ __|
#  | || | | | ||  __/ |  | |_) | | |  __/ |_
# |___|_| |_|\__\___|_|  | .__/|_|  \___|\__|
#                        |_|

class VType(Enum):
  Int=0
  Tuple=1
  Lam=2
  Bool=3
  Err=4
  Nil=5
  Ap=6
  Ref=7
  Op=8

@dataclass(frozen=True)
class Val:
  typ:VType
  val:'ValUnion'

@dataclass(frozen=True)
class Err:
  msg:str

@dataclass(frozen=True)
class Nil:
  pass

@dataclass(frozen=True)
class Ap:
  f:Val
  x:Val

@dataclass(frozen=True)
class Lam:
  pat:Ref
  body:Val

@dataclass
class Op:
  term:Term
  bind:List[Ref]

ValUnion=Union[int,Tuple[Val,Val],Lam,bool,Err,Nil,Ap,Ref,Op]

def mklam(body:Callable[[Ref],Val])->Val:
  ref=newref()
  return Val(VType.Lam, Lam(ref,body(ref)))

def asint(v:Val)->int:
  assert isinstance(v,Val)
  if v.typ!=VType.Int:
    raise ValueError(f"{v} is not an int!")
  assert isinstance(v.val,int), f"{v}"
  return int(v.val)

def astuple(v:Val)->Tuple[Val,Val]:
  assert isinstance(v,Val)
  if v.typ!=VType.Tuple:
    raise ValueError(f"{v} is not a tuple!")
  assert isinstance(v.val,tuple), f"{v}"
  return v.val


Stack=List[Val]

def mkint(i:int)->Val:
  return Val(VType.Int, i)

def mkbool(b:bool)->Val:
  return Val(VType.Bool, b)

def mktuple(a:Val,b:Val)->Val:
  return Val(VType.Tuple, (a,b))

def mknil()->Val:
  return Val(VType.Nil, Nil())

def mkop(t:Term, binds:List[Ref])->Val:
  return Val(VType.Op, Op(t,binds))

def mkap(f:Val, x:Val)->Val:
  return Val(VType.Ap, Ap(f,x))

def mkvref(r:Ref)->Val:
  return Val(VType.Ref, r)

def pval(v:Val)->str:
  if v.typ==VType.Int:
    return str(v.val)
  elif v.typ==VType.Tuple:
    return f"({pval(v.val[0])},{pval(v.val[1])})"
  elif v.typ==VType.Lam:
    return f"({v.val.pat.to} -> {pval(v.val.body)})"
  elif v.typ==VType.Bool:
    return 't' if bool(v.val) else 'f'
  elif v.typ==VType.Err:
    return 'E'
  elif v.typ==VType.Nil:
    return 'nil'
  elif v.typ==VType.Ap:
    return f"({pval(v.val.f)} {pval(v.val.x)})"
  elif v.typ==VType.Ref:
    return v.val.to
  elif v.typ==VType.Op:
    return f"{v.val.term.name} {' '.join([r.to for r in v.val.bind])}"
  else:
    assert False, f"{v}"


def checkerr(vals, lam)->Val:
  """ DEPRECATED"""
  for v in vals:
    assert isinstance(v, Val)
    if v.typ==VType.Err:
      return v
  return lam(*vals)

# def chkerr1(lam:Callable[[Ref],Val])->Callable[[Ref],Val]:
#   def _lam(v:Val)->Val:
#     assert isinstance(v, Val)
#     if v.typ==VType.Err:
#       return v
#     else:
#       return lam(v)
#   return _lam

def div_c0(a, b):
  if (a >= 0) != (b >= 0) and a % b:
    return a // b + 1
  else:
    return a // b

def _ERR(msg):
  set_trace()
  return Val(VType.Err, msg)

# FIXME: typed interpretation may reject some programs, like pwr2
# _T = Val(VType.Bool, True)
# _F = Val(VType.Bool, False)
# _NIL = mknil()
_T = mklam(lambda a: mklam(lambda b: mkvref(a)))
_F = mklam(lambda a: mklam(lambda b: mkvref(b)))
_NIL = mklam(lambda a: _T)

# def isnil(v:Val)->bool:
#   if v.typ!=VType.Lam:
#     return False

def load_expr(expr:List[Token])->Val:
  def _lam1(op):
    return mklam(lambda a: mkop(op,[a]))
  def _lam2(op):
    return mklam(lambda a: mklam(lambda b: mkop(op,[a,b])))
  def _lam3(op):
    return mklam(lambda a: mklam(lambda b: mklam(lambda c: mkop(op,[a,b,c]))))
  stack:Stack=[]
  for t in reversed(expr):
    assert isinstance(t,Token)
    if t.typ==TType.Int:
      assert isinstance(t.val, int)
      stack.append(Val(VType.Int, t.val))
    elif t.typ==TType.Ref:
      assert isinstance(t.val, Ref)
      stack.append(Val(VType.Ref, t.val))
    elif t.typ==TType.Term:
      assert isinstance(t.val, Term)
      if t.val==T:
        stack.append(_T)
      elif t.val==F:
        stack.append(_F)
      elif t.val==nil:
        stack.append(_NIL)
      elif t.val==ap:
        f=stack.pop()
        x=stack.pop()
        stack.append(mkap(f,x))
      else:
        if t.val.nargs==1:
          stack.append(_lam1(t.val))
        elif t.val.nargs==2:
          stack.append(_lam2(t.val))
        elif t.val.nargs==3:
          stack.append(_lam3(t.val))
        else:
          raise ValueError(f"Cant deal with {t}, Help!")
    else:
      raise ValueError(f"Unsupported token type '{t.typ}'")
  assert len(stack)==1, f"{[pval(x) for x in stack]}"
  return stack[0]




Memspace=Dict[Ref,Val]

@dataclass
class Memory:
  space:Memspace

def mkmem()->Memory:
  return Memory({})

STATE:Memory=Memory({})

def pprog(p:dict)->str:
  acc=[]
  for ref,val in p.items():
    acc.append(f"{ref.to} = {pval(val)}")
  return '\n'.join(acc)

def pmem(m:Memory)->str:
  return pprog(m.space)

def ppr(x:Any)->None:
  if isinstance(x,Memory):
    print(pmem(x))
  elif isinstance(x,Val):
    print(pval(x))
  elif isinstance(x,dict):
    print(pprog(x))
  else:
    assert False, f"Can't print {x}, Help!"

def load_program(m:Memory, src:str):
  """ Mutatas existing memory or builds a new one by adding new expressions """
  p=parse_program(src)
  for i,(ref,expr) in enumerate(p.body.items()):
    v=load_expr(expr)
    m.space[ref]=v

def isnf(v:Val)->bool:
  # Fixme: waht about some Ops, like cobinators?
  if v.typ in [VType.Ap, VType.Ref, VType.Op]:
    return False
  return True

def interp(m:Memory, target:Ref, h:Optional[Memspace]=None)->Tuple[Val,Memspace]:
  heap={} if h is None else h
  queue:List[Ref]=[]

  def _getmem(r:Ref)->Val:
    while True:
      v=heap.get(r, m.space.get(r,None))
      if v is None:
        set_trace()
      if v.typ==VType.Ref:
        r=v.val
      else:
        return v

  def _addqueue(v:Ref)->None:
    nonlocal queue
    if v in queue:
      print(f'Recursion detected on {v}')
    queue.append(v)

  _addqueue(target)
  while len(queue)>0:

    # set_trace()

    cur=queue.pop();
    v=_getmem(cur)

    def _nfn(r:Ref)->bool:
      """ _NOT_ in normal form, with effect """
      if not isnf(_getmem(r)):
        _addqueue(cur)
        _addqueue(r)
        return True
      return False


    if v.typ==VType.Ap:
      assert isinstance(v.val, Ap)
      branches:List[Val]=[]
      matched:Dict[Ref,Val]=OrderedDict()
      while v.typ==VType.Ap or v.typ==VType.Ref:
        if v.typ==VType.Ref:
          v=_getmem(v.val)
          continue
        assert isinstance(v.val, Ap)
        branches.append(v.val.x)
        v=v.val.f
      while v.typ==VType.Lam:
        assert isinstance(v.val, Lam)
        if len(branches)==0:
          break
        matched[v.val.pat]=branches.pop()
        v=v.val.body

      if v.typ in [VType.Int, VType.Bool, VType.Tuple, VType.Err, VType.Nil]:
        raise ValueError(f"Error! Can't apply to '{pval(v)}'")

      # Split current target in two
      ref=newref('e')
      v2=mkvref(ref)
      for b in reversed(branches):
        v2=mkap(v2,b)
      _addqueue(cur)
      heap[cur]=v2

      # Leaf `v` with matched patterns
      _addqueue(ref)
      heap[ref]=v

      # Arguments of `v`
      for ref,val in matched.items():
        # _addqueue(ref)
        heap[ref]=val
    elif v.typ==VType.Op:
      assert isinstance(v.val, Op)
      o:Op=v.val
      r=o.bind
      a=[_getmem(i) for i in o.bind]
      try:
        if o.term==neg:
          if _nfn(r[0]):
            continue
          heap[cur]=mkint(-asint(a[0]))
        elif o.term==inc:
          if _nfn(r[0]):
            continue
          heap[cur]=mkint(asint(a[0])+1)
        elif o.term==dec:
          if _nfn(r[0]):
            continue
          heap[cur]=mkint(asint(a[0])-1)
        elif o.term==pwr2:
          if _nfn(r[0]):
            continue
          if asint(a[0])<0:
            heap[cur]=_ERR('pwr2 arg is less than zero')
          else:
            heap[cur]=mkint(2**asint(a[0]))
        elif o.term==add:
          if _nfn(r[0]) or _nfn(r[1]):
            continue
          heap[cur]=mkint(asint(a[0])+asint(a[1]))
        elif o.term==mul:
          if _nfn(r[0]) or _nfn(r[1]):
            continue
          heap[cur]=mkint(asint(a[0])*asint(a[1]))
        elif o.term==div:
          if _nfn(r[0]) or _nfn(r[1]):
            continue
          heap[cur]=mkint(div_c0(asint(a[0]),asint(a[1])))
        elif o.term==eq:
          if _nfn(r[0]) or _nfn(r[1]):
            continue
          if a[0].typ==a[1].typ:
            heap[cur]=_T if a[0].val==a[1].val else _F
          else:
            heap[cur]=_F
        elif o.term==C:
          heap[cur]=mkap(mkap(a[0],a[1]),a[2])
        elif o.term==S:
          heap[cur]=mkap(mkap(a[0],a[2]),mkap(a[1],a[2]))
        elif o.term==B:
          heap[cur]=mkap(a[0],mkap(a[1],a[2]))
        elif o.term==I:
          heap[cur]=a[0]
        elif o.term==cons:
          # if _nfn(r[0]) or _nfn(r[1]):
          #   continue
          # heap[cur]=mktuple(a[0],a[1])
          heap[cur]=mkap(mkap(a[2],a[0]),a[1])
        elif o.term==car:
          # if _nfn(r[0]):
          #   continue
          # heap[cur]=astuple(a[0])[0]
          heap[cur]=mkap(a[0],_T)
        elif o.term==cdr:
          # if _nfn(r[0]):
          #   continue
          # heap[cur]=astuple(a[0])[1]
          heap[cur]=mkap(a[0],_F)
        elif o.term==isnil:
          # if _nfn(r[0]):
          #   continue
          # set_trace() FIXME: how to implement in car/cdr?
          # heap[cur]=_T if a[0]==_NIL else _F
          heap[cur]=mkap(a[0],mkap(_T, mkap(_T,_F)))
        elif o.term==if0:
          if _nfn(r[0]):
            continue
          heap[cur]=a[1] if asint(a[0])==0 else a[2]
        else:
          raise NotImplementedError(f"Can't op {o}, Help!")
      except ValueError as e:
        heap[cur]=_ERR(str(e))

    elif v.typ==VType.Int or v.typ==VType.Bool or \
         v.typ==VType.Lam or v.typ==VType.Tuple or \
         v.typ==VType.Nil:
      pass
    elif v.typ==VType.Ref:
      assert False, f"Unexpected ref {v}"
    elif v.typ==VType.Err:
      set_trace()
      pass
    else:
      raise NotImplementedError(f"Can't value {v}, Help!")

  return _getmem(target), heap

def interp_expr(v:Val)->Tuple[Val,Memspace]:
  m=Memory({mkref('tgt'):v})
  return interp(m,mkref('tgt'))


# def interp(v:Val)->Val:
#   assert isinstance(v,Val), f"{v}"
#   while True:
#     if v.typ==VType.Ap:
#       assert isinstance(v.val,Ap)
#       v=call(v.val.f,v.val.x)
#     elif v.typ==VType.Ref:
#       assert isinstance(v.val,Ref)
#       v=STATE.mem[v.val]
#     else:
#       return v

# def call(f:Val, v:Val)->Val:
#   assert isinstance(f,Val) and isinstance(v,Val)
#   f=force(f)
#   v=force(v)
#   assert f.typ==VType.Lam, f"{f}"
#   assert isinstance(f.val,Lam)
#   return f.val.fn(v)



# def run_program(name:str, s:Memory)->Val:
#   global STATE
#   STATE=s
#   return interp(STATE.mem[mkref(name)])


# def interp(p:str, s0=None)->Memory:
#   return interp_program(parse_program(p), s0)

def run_test(hint:str, test:str)->None:
  print(f"Testing {hint}")
  for i,tl in enumerate(test.split('\n')):
    if len(tl.strip())==0 or tl.strip()[0]=='#':
      continue
    print(f"Checking line {i:02d}: {tl.strip()}")
    pos= not ('!=' in tl)
    expr_test,expr_ans=tl.split('=' if pos else '!=')
    try:
      val_test=load_expr(parse_expr(expr_test))
      val_ans=load_expr(parse_expr(expr_ans))

      redex_test,_=interp_expr(val_test)
      redex_ans,_=interp_expr(val_ans)
      if pos:
        assert redex_test==redex_ans, f"{pval(redex_test)} != {pval(redex_ans)}"
      else:
        set_trace()
        assert redex_test!=redex_ans, (f"{pval(redex_test)} == {pval(redex_ans)}, "
                                      "but it shouldn't")
    except KeyboardInterrupt:
      raise
    except AssertionError:
      raise
    except Exception as e:
      if pos:
        raise

def prog_test(prog:str, expr:str)->None:
  m=Memory({})
  load_program(m,prog)
  redex_test,_=interp(m,list(m.space.keys())[-1])
  redex_ans,_=interp_expr(load_expr(parse_expr(expr)))
  assert redex_test==redex_ans, f"{pval(redex_test)} != {pval(redex_ans)}"


#  __  __           _
# |  \/  | ___   __| | ___ _ __ ___
# | |\/| |/ _ \ / _` |/ _ \ '_ ` _ \
# | |  | | (_) | (_| |  __/ | | | | |
# |_|  |_|\___/ \__,_|\___|_| |_| |_|


Bit=int

@dataclass(frozen=True)
class ModulatedVal:
  # body:List[Bit] # like [0,1,0,1,...]
  body:str # "01010101 ..."


def nbits(i:int)->int:
  acc=0
  while i>0:
    i=i>>1
    acc+=1
  return acc

def nbits_mod4(i:int)->int:
  return ((nbits(i)-1)//4)+1 if i>0 else 0

def mod_int(i:int)->ModulatedVal:
  acc=""
  acc+=("01" if i>=0 else "10")
  i=i if i>=0 else -i
  nbits=nbits_mod4(i)
  acc+=(nbits*"1")+"0"
  acc+=str(format(i,'b').zfill(4*nbits) if i>0 else '')
  return ModulatedVal(acc)


def mod_val(v:Val)->ModulatedVal:
  acc=""
  if v.typ==VType.Tuple:
    acc+="11"
    assert isinstance(v.val, tuple)
    acc+=mod_val(v.val[0]).body
    acc+=mod_val(v.val[1]).body
  elif v.typ==VType.Nil:
    acc+="00"
  elif v.typ==VType.Int:
    assert isinstance(v.val, int)
    acc+=mod_int(v.val).body
  else:
    raise ValueError(f"Can't modulate {v}")
  return ModulatedVal(acc)


def dem_int(s:str)->Tuple[int,int]:
  """ Returns answer and num_bits parsed """
  sign=1 if s[:2]=="01" else -1
  nbits4=0
  i=2
  while s[i]=='1':
    nbits4+=1; i+=1
  if nbits4==0:
    return (0,3)
  i+=1 # pass last zero
  num=s[i:i+nbits4*4]
  # print('s', s, 'i',i ,'nbits4', nbits4, 'num:',num)
  return (sign*int(num, 2), i+nbits4*4)

def dem_val(s:str)->Tuple[Val,int]:
  assert len(s)>=2, f"Cant decode {s}"
  if s[:2]=="11":
    a,sz=dem_val(s[2:])
    b,sz2=dem_val(s[2+sz:])
    return (mktuple(a,b),2+sz+sz2)
  elif s[:2]=="00":
    return mknil(),2
  else:
    i,sz=dem_int(s)
    return mkint(i),sz


# from solution.api import api_send
# def interact(protocol:Program, state:Val, vector:Val):
#   """ A draft """
#   while True:
#     flag,state2,data=interpret(protocol,state,vector)
#     if flag.val==0:
#       return state2, interpret(multipledraw,data)
#     vector=api_send(mod_val(data))
#     state=state2










