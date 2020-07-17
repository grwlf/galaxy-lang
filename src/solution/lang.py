from typing import ( Union, List, Optional, Any, Callable, Dict, Tuple )
from dataclasses import dataclass
from collections import OrderedDict
from ipdb import set_trace


OPS:Dict[str,'Op']={}
collect_ops:bool=True

@dataclass(frozen=True, eq=True)
class Op:
  name:str
  nargs:int

  def __post_init__(self):
    if collect_ops:
      global OPS
      assert self.name not in OPS
      OPS[self.name]=self

T=Op('t',0)
F=Op('f',0)
inc=Op('inc',1)
dec=Op('dec',1)
add=Op('add',2)
mul=Op('mul',2)
div=Op('div',2)
eq=Op('eq',2)
lt=Op('lt',2)
mod=Op('mod',1) # has a list version
dem=Op('dem',1)
send=Op('send',1)
neg=Op('neg',1)
ap=Op('ap',2)
S=Op('s',3)
C=Op('c',3)
B=Op('b',3)
pwr2=Op('pwr2',2)
I=Op('i',1)
cons=Op('cons',2)
car=Op('car',2)
cdr=Op('cdr',2)
nil=Op('nil',1)
isnil=Op('isnil',1)
draw=Op('draw',1) # [x,y]->img
checkerboard=Op('checkerboard',2)
multipledraw=Op('multipledraw',1) # [x]->img???
if0=Op('if0',3)
collect_ops=False

def isop(s:str)->bool:
  return s in set(OPS.keys())

def mkop(s:str)->Op:
  return OPS[s]

from enum import Enum
class TType(Enum):
  Int=0
  List=2
  Op=3
  Ref=4

Picture=List[Tuple[int,int]]

@dataclass(frozen=True)
class Ref:
  to:str

def isref(s:str)->bool:
  if s=='galaxy':
    return True
  else:
    return s[0]==':' and str(int(s[1:]))==s[1:]

def mkref(s:str)->Ref:
  assert isref(s)
  return Ref(s)

@dataclass
class Token:
  typ:TType
  val:Union[int,list,Op,Ref]

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

@dataclass
class Assign:
  name:Ref
  expr:List[Token]

def parse_expr(line:List[Word])->List[Token]:
  acc=[]
  for w in line:
    if isint(w):
      acc.append(Token(TType.Int, int(w)))
    elif isref(w):
      acc.append(Token(TType.Ref, mkref(w)))
    elif isop(w):
      acc.append(Token(TType.Op, mkop(w)))
    else:
      raise ValueError(f'Unknown expr token "{w}"')
  return acc

def parse_assign(line:Line)->Assign:
  assert_isline(line)
  ws=line
  ref=mkref(ws[0])
  assert ws[1]=='='
  expr=parse_expr(ws[2:])
  return Assign(ref,expr)

@dataclass
class Program:
  body:Dict[Ref,Assign]


def parse_program(src:str)->Program:
  acc=OrderedDict()
  lines=src.split('\n')
  for l in lines:
    ws=l.split()
    a=parse_assign(ws)
    acc[a.name]=a
  return Program(acc)


class Lam:
  def __init__(self, fn:Callable[['Val'],'Val'], bool_val:Optional[bool]=None):
    self.fn:Callable[['Val'],'Val']=fn
    self.bool_val:Optional[bool]=bool_val

  def __eq__(self, other)->bool:
    if self.bool_val is not None and other.bool_val is not None:
      return self.bool_val and other.bool_val
    raise ValueError("Can't compare this lambdas")

class VType(Enum):
  Int=0
  Pic=1
  List=2
  TLam=3
  Bool=4

@dataclass(frozen=True)
class Val:
  typ:VType
  val:Union[int,Picture,list,Lam,bool]

Stack=List[Val]

@dataclass
class State:
  v:Dict[Ref,Stack]

def mkstate0()->State:
  return State({})

def asint(v:Val)->int:
  assert isinstance(v,Val)
  assert v.typ==VType.Int
  # FIXME assert isinstance(v.val,int), f"{v.val}"
  return int(v.val)

def aslam(v:Val)->Callable[[Val],Val]:
  assert isinstance(v,Val)
  assert v.typ==VType.TLam, f"{v.typ}"
  assert isinstance(v.val,Lam)
  return v.val.fn


def div_c0(a, b):
  if (a >= 0) != (b >= 0) and a % b:
    return a // b + 1
  else:
    return a // b

_T = Val(VType.TLam, Lam(lambda a: Val(VType.TLam, Lam(lambda b: a))))
_F = Val(VType.TLam, Lam(lambda a: Val(VType.TLam, Lam(lambda b: b))))

def interp_expr(expr:List[Token], s:State)->Stack:
  stack:Stack=[]
  for t in reversed(expr):
    assert isinstance(t,Token)
    if t.typ==TType.Int:
      assert isinstance(t.val, int)
      stack.append(Val(VType.Int, t.val))
    elif t.typ==TType.Ref:
      assert isinstance(t.val, Ref)
      stack.extend(list(s.v[t.val]))
    elif t.typ==TType.Op:
      assert isinstance(t.val, Op)
      if t.val==T:
        stack.append(_T)
        # stack.append(Val(VType.Bool,True))
      elif t.val==F:
        stack.append(_F)
        # stack.append(Val(VType.Bool,False))
      elif t.val==eq:
        def _eq(a,b):
          assert a.typ==b.typ
          if a.val==b.val:
            return _T
          else:
            return _F
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: _eq(a,b))))))
      elif t.val==mul:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.Int, asint(a)*asint(b)))))))
      elif t.val==add:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.Int, asint(a)+asint(b)))))))
      elif t.val==div:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.Int, div_c0(asint(a),asint(b))))))))
      elif t.val==neg:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.Int, -asint(a)))))
      elif t.val==inc:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.Int, asint(a)+1))))
      elif t.val==dec:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.Int, asint(a)-1))))
      elif t.val==pwr2:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.Int, 2**asint(a)))))
      elif t.val==C:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.TLam,
                         Lam(lambda c:
                           aslam(aslam(a)(c))(b)
                         )))))))
      elif t.val==S:
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: Val(VType.TLam,
                         Lam(lambda x2:
                           aslam(aslam(x0)(x2))( aslam(x1)(x2) )
                         )))))))
      elif t.val==B:
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: Val(VType.TLam,
                         Lam(lambda x2:
                           aslam(x0)(aslam(x1)(x2))
                         )))))))
      elif t.val==ap:
        l=stack.pop()
        assert l.typ==VType.TLam
        x=stack.pop()
        assert isinstance(l.val,Lam)
        r=l.val.fn(x)
        stack.append(r)
      else:
        raise ValueError(f"Unsupported token op '{t.val}'")
    else:
      raise ValueError(f"Unsupported token type '{t.typ}'")
  return stack

def interp_assign(a:Assign, s:State)->State:
  stack=interp_expr(a.expr, s)
  s.v[a.name]=stack
  return s


def interp_program(p:Program, s0_:Optional[State]=None)->State:
  s:State=s0_ if s0_ is not None else mkstate0()
  for i,(aref,a) in enumerate(p.body.items()):
    interp_assign(a,s)
  return s

def interp(p:str, s0=None)->State:
  return interp_program(parse_program(p), s0)

def interp_test(hint:str, test:str)->None:
  print(f"Testing {hint}")
  for i,tl in enumerate(test.split('\n')):
    if len(tl.strip())==0 or tl.strip()[0]=='#':
      continue
    print(f"Checking line {i:02d}: {tl.strip()}")
    expr_test,expr_ans=tl.split('=')
    val_test=interp_expr(parse_expr(expr_test.split()),mkstate0())
    val_ans=interp_expr(parse_expr(expr_ans.split()),mkstate0())
    assert val_test is not val_ans
    assert val_test==val_ans, f"{val_test} != {val_ans}"


#   pass

