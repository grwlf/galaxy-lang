from typing import ( Union, List, Optional, Any, Callable, Dict, Tuple )
from dataclasses import dataclass


OPS:Dict[str,'Op']={}
collect_ops:bool=True

@dataclass
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
Add=Op('add',2)
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
  val:Union[int,Picture,list,Op,Ref]

def isint(w:str)->bool:
  try:
    return str(int(w))==w
  except ValueError:
    return False

Word=str
Line=List[Word]
Source=List[str]

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
      acc.append(Token(TType.Int,w))
    elif isref(w):
      acc.append(mkref(w))
    elif isop(w):
      acc.append(mkop(w))
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


def parse_galaxy(src:Source)->Program:
  acc={}
  lines=src.split('\n')
  for l in lines:
    ws=l.split()
    a=parse_assign(ws)
    acc[a.name]=a
  return Program(acc)



class VType(Enum):
  Int=0
  Pic=1
  List=2

@dataclass
class Val:
  typ:VType
  val:Union[int,Picture,list]

@dataclass
class State:
  v:Dict[str,Val]

# def interp(code:Source, s0:State)->State:
#   lines=code.split('\n')
#   pass

