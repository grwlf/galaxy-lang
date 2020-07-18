from typing import ( Union, List, Optional, Any, Callable, Dict, Tuple )
from dataclasses import dataclass
from collections import OrderedDict
from ipdb import set_trace


#  ____
# |  _ \ __ _ _ __ ___  ___
# | |_) / _` | '__/ __|/ _ \
# |  __/ (_| | |  \__ \  __/
# |_|   \__,_|_|  |___/\___|


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
vec=Op('vec',2)
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
  """ Token types"""
  Int=0
  List=2
  Op=3
  Ref=4

@dataclass
class Picture:
  data:List[Tuple[int,int]]

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
    elif isop(w):
      acc.append(Token(TType.Op, mkop(w)))
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
  Pic=1
  Tuple=2
  TLam=3
  Bool=4
  TErr=5
  Nil=6
  Thunk=7
  Ref=8

ValUnion=Union[int,Picture,Tuple['Val','Val'],'Lam',bool,'Err','Nil','Thunk',Ref]

@dataclass(frozen=True)
class Val:
  typ:VType
  val:ValUnion

@dataclass(frozen=True)
class Err:
  msg:str

@dataclass(frozen=True)
class Nil:
  pass

@dataclass(frozen=True)
class Thunk:
  f:Val
  x:Val

class Lam:
  def __init__(self, fn:Callable[[Val],Val]):
    self.fn:Callable[[Val],Val]=fn


@dataclass
class State:
  mem:Dict[Ref,Val]


STATE:State=State({})

def asint(v:Val)->int:
  assert isinstance(v,Val)
  assert v.typ==VType.Int, f"{v.typ}"
  assert isinstance(v.val,int), f"{v.val}"
  return int(v.val)

def force(v:Val)->Val:
  assert isinstance(v,Val), f"{v}"
  while True:
    if v.typ==VType.Thunk:
      assert isinstance(v.val,Thunk)
      v=call(v.val.f,v.val.x)
    elif v.typ==VType.Ref:
      assert isinstance(v.val,Ref)
      v=STATE.mem[v.val]
    else:
      return v

def call(f:Val, v:Val)->Val:
  assert isinstance(f,Val) and isinstance(v,Val)
  f=force(f)
  v=force(v)
  assert f.typ==VType.TLam, f"{f}"
  assert isinstance(f.val,Lam)
  return f.val.fn(v)

Stack=List[Val]

def mkint(i:int)->Val:
  return Val(VType.Int, i)

def mktuple(a:Val,b:Val)->Val:
  return Val(VType.Tuple, (a,b))

def mknil()->Val:
  return Val(VType.Nil, Nil())

def mkstate0()->State:
  return State({})

def checkerr(vals, lam)->Val:
  """ DEPRECATED"""
  for v in vals:
    assert isinstance(v, Val)
    if v.typ==VType.TErr:
      return v
  return lam(*vals)

def chkerr1(lam:Callable[[Val],Val])->Callable[[Val],Val]:
  def _lam(v:Val)->Val:
    assert isinstance(v, Val)
    if v.typ==VType.TErr:
      return v
    else:
      return lam(v)
  return _lam


def div_c0(a, b):
  if (a >= 0) != (b >= 0) and a % b:
    return a // b + 1
  else:
    return a // b


_ERR = lambda msg : Val(VType.TErr, msg)

# FIXME: typed interpretation may reject some programs, like pwr2
_T = Val(VType.Bool, True)
_F = Val(VType.Bool, False)
# _T = Val(VType.TLam, Lam(lambda a: Val(VType.TLam, Lam(lambda b: a))))
# _F = Val(VType.TLam, Lam(lambda a: Val(VType.TLam, Lam(lambda b: b))))

def interp_expr(expr:List[Token], s:State)->Stack:
  stack:Stack=[]
  for t in reversed(expr):
    assert isinstance(t,Token), f"{t}"
    if t.typ==TType.Int:
      assert isinstance(t.val, int)
      stack.append(Val(VType.Int, t.val))
    elif t.typ==TType.Ref:
      assert isinstance(t.val, Ref)
      stack.append(Val(VType.Ref, t.val))
    elif t.typ==TType.Op:
      assert isinstance(t.val, Op)
      if t.val==T:
        stack.append(_T)
      elif t.val==F:
        stack.append(_F)
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
      elif t.val==lt:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b:
                           checkerr([a,b], lambda a,b:
                             Val(VType.Bool, asint(a)<asint(b))))))))
      elif t.val==mul:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b:
                           checkerr([a,b], lambda a,b:
                             Val(VType.Int,asint(a)*asint(b))))))))
      elif t.val==add:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.Int, asint(a)+asint(b)))))))
      elif t.val==div:
        def _div(a,b):
          if b.typ==VType.Int and int(b.val)==0:
            return _ERR(f"Division by zero")
          return checkerr([a,b], lambda a,b: div_c0(asint(a),asint(b)))
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.Int,_div(a,b)))))))
      elif t.val==neg:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.Int, -asint(a)))))
      elif t.val==inc:
        stack.append(Val(VType.TLam,
                         Lam(lambda a:
                           checkerr([a], lambda a: Val(VType.Int, asint(a)+1)))))
      elif t.val==dec:
        stack.append(Val(VType.TLam,
                         Lam(lambda a:
                           checkerr([a], lambda a: Val(VType.Int,asint(a)-1)))))
      elif t.val==pwr2:
        def _pwr2(v):
          if v.typ==VType.Int and int(v.val)<0:
            return _ERR(f"pwr2: {v.val}<0")
          else:
            return Val(VType.Int, checkerr([v], lambda v: 2**asint(v)))
        stack.append(Val(VType.TLam, Lam(_pwr2)))
      elif t.val==C:
        stack.append(Val(VType.TLam,
                         Lam(lambda a: Val(VType.TLam,
                         Lam(lambda b: Val(VType.TLam,
                         Lam(lambda c:
                           call(call(a,c),b)
                         )))))))
      elif t.val==S:
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: Val(VType.TLam,
                         Lam(lambda x2:
                           call(call(x0,x2),call(x1,x2))
                         )))))))
      elif t.val==B:
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: Val(VType.TLam,
                         Lam(lambda x2:
                           call(x0,call(x1,x2))
                         )))))))
      elif t.val==I:
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: x0)))
      elif t.val==nil:
        _e:List[Val]=[]
        stack.append(Val(VType.Nil, Nil()))
      elif t.val==cons or t.val==vec:
        def _cons(x0,x1)->Val:
          assert isinstance(x0,Val) and isinstance(x1,Val)
          return Val(VType.Tuple, (x0,x1))
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: checkerr([x0,x1], _cons))))))
      elif t.val==car:
        def _car(x0:Val)->Val:
          assert isinstance(x0,Val)
          assert x0.typ==VType.Tuple
          assert isinstance(x0.val,tuple)
          return x0.val[0]
        stack.append(Val(VType.TLam, Lam(chkerr1(_car))))

      elif t.val==cdr:
        def _cdr(x0:Val)->Val:
          assert isinstance(x0,Val)
          assert x0.typ==VType.Tuple
          assert isinstance(x0.val,tuple)
          return x0.val[1]
        stack.append(Val(VType.TLam, Lam(chkerr1(_cdr))))

      elif t.val==isnil:
        def _isnil(v:Val)->Val:
          return _T if v.typ==VType.Nil else _F
        stack.append(Val(VType.TLam, Lam(chkerr1(_isnil))))

      elif t.val==if0:
        # def _isnil(v):
        #   if v.typ!=VType.List:
        #     return _ERR(f"Expected list, but got {v.typ}")
        #   assert isinstance(v.val,list)
        #   return _T if len(v.val)==0 else _F
        # stack.append(Val(VType.TLam, Lam(chkerr1(_isnil))))
        def _if0(c:Val,t:Val,f:Val)->Val:
          if c.typ!=VType.Int:
            return _ERR(f"if0: expected int, got '{c}'")
          assert isinstance(c.val,int)
          return t if c.val==0 else f
        stack.append(Val(VType.TLam,
                         Lam(lambda x0: Val(VType.TLam,
                         Lam(lambda x1: Val(VType.TLam,
                         Lam(lambda x2: checkerr([x0,x1,x2], _if0)
                         )))))))

      elif t.val==ap:
        f=stack.pop()
        x=stack.pop()
        stack.append(Val(VType.Thunk, Thunk(f,x)))
      else:
        raise ValueError(f"Unsupported token op '{t.val}'")
    else:
      raise ValueError(f"Unsupported token type '{t.typ}'")
  return stack


def interp_program(src:str, s0_:Optional[State]=None)->State:
  p=parse_program(src)
  s:State=s0_ if s0_ is not None else mkstate0()
  for i,(ref,expr) in enumerate(p.body.items()):
    stack=interp_expr(expr, s)
    assert len(stack)==1, f"{stack}"
    s.mem[ref]=stack[0]
  return s


def run_program(name:str, s:State)->Val:
  global STATE
  STATE=s
  return force(STATE.mem[mkref(name)])


# def interp(p:str, s0=None)->State:
#   return interp_program(parse_program(p), s0)

def interp_test(hint:str, test:str)->None:
  print(f"Testing {hint}")
  for i,tl in enumerate(test.split('\n')):
    if len(tl.strip())==0 or tl.strip()[0]=='#':
      continue
    print(f"Checking line {i:02d}: {tl.strip()}")
    expr_test,expr_ans=tl.split('=')
    stack_test=interp_expr(parse_expr(expr_test),mkstate0())
    stack_ans=interp_expr(parse_expr(expr_ans),mkstate0())
    assert len(stack_test)==1, f"len({stack_test})=={len(stack_test)}"
    assert len(stack_ans)==1, f"{stack_ans}"
    val_test=force(stack_test[0])
    val_ans=force(stack_ans[0])
    # assert val_test is not val_ans, f"{val_test}, {val_ans}"
    assert val_test==val_ans, f"{val_test} != {val_ans}"





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










