
from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName, Example, IMem, IExpr, IAp, ILam,
                          IError, IVal, IMem, Example)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin

from galang.serbin_pb2 import Node, Value, Tuple as PBTuple, List as PBList

from typing import List, Any, Callable
from enum import IntEnum, unique

BIN=Any

@unique
class Tag(IntEnum):
  unknown = 0
  # Expr
  val = 100
  lam = 101
  let = 102
  ap = 103
  intrin = 104
  const = 105
  ref = 106
  # IExpr
  iap = 200
  ilam = 201
  ierror = 202
  ival = 203
  # IMem
  imem = 300
  # Example
  example = 400
  examples = 401


def _flat(v):
  return ' '.join(str(v).split())

def _node(tag, value):
  n=Node()
  n.tag = int(tag)
  n.value.CopyFrom(value)
  return n

def _tuple(v1,v2):
  assert isinstance(v1,Value)
  assert isinstance(v2,Value)
  t=PBTuple()
  t.v1.CopyFrom(v1)
  t.v2.CopyFrom(v2)
  return t

def _list(ls):
  l=PBList()
  for i in ls:
    assert isinstance(i,Value)
    v=l.list.add()
    v.CopyFrom(i)
  return l

def _value(v):
  value=Value()
  if isinstance(v,Node):
    value.node.CopyFrom(v)
  elif isinstance(v,str):
    value.string=v
  elif isinstance(v,int):
    value.int64=v
  elif isinstance(v,tuple):
    assert len(v)==2
    t=_tuple(v[0],v[1])
    value.tuple.CopyFrom(t)
  elif isinstance(v,list):
    l=_list(v)
    value.list.CopyFrom(l)
  else:
    raise ValueError(f"Invalid value's ({_flat(v)}) type: {str(type(v))}")
  return value

def expr2bin(e:Expr)->BIN:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return _node(Tag.val, _value(_node(Tag.const, _value(e.val.const))))
    elif isinstance(e.val, Ref):
      return _node(Tag.val, _value(_node(Tag.ref, _value(e.val.name))))
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return _node(Tag.lam, _value((_value(e.name),
                                   _value(expr2bin(e.body)))))
  elif isinstance(e, Let):
    return _node(Tag.let, _value((_value(e.ref.name),
                                   _value((_value(expr2bin(e.expr)),
                                           _value(expr2bin(e.body)))))))
  elif isinstance(e, Ap):
    return _node(Tag.ap, _value((_value(expr2bin(e.func)),
                                  _value(expr2bin(e.arg)))))
  elif isinstance(e, Intrin):
    return _node(Tag.intrin, _value((_value(e.name.val),
                                      _value([_value((_value(n),
                                                      _value(expr2bin(a))))
                                             for n,a in e.args.dict.items()]))))
  else:
    raise ValueError(f"Invalid expression {e}")

def bin2expr(j:BIN)->Expr:
  typ = j.tag
  if typ == Tag.val:
    vtyp = j.value.node.tag
    if vtyp == Tag.const:
      return num(j.value.node.value.int64)
    elif vtyp == Tag.ref:
      return ref(j.value.node.value.string)
    else:
      raise ValueError(f"Invalid value expression {_flat(j)}")
  elif typ==Tag.lam:
    return lam(j.value.tuple.v1.string, lambda _: bin2expr(j.value.tuple.v2.node))
  elif typ==Tag.let:
    return let_(j.value.tuple.v1.string,
                          bin2expr(j.value.tuple.v2.tuple.v1.node),
                lambda _: bin2expr(j.value.tuple.v2.tuple.v2.node))
  elif typ==Tag.ap:
    return ap(bin2expr(j.value.tuple.v1.node),
              bin2expr(j.value.tuple.v2.node))
  elif typ==Tag.intrin:
    return intrin(MethodName(j.value.tuple.v1.string),
                  [(         v.tuple.v1.string,
                    bin2expr(v.tuple.v2.node)) for v in j.value.tuple.v2.list.list])
  else:
    raise ValueError(f"Invalid expression {_flat(j)}")


def iexpr2bin(e:IExpr)->dict:
  if isinstance(e, IVal):
    if isinstance(e.val, int):
      return _node(Tag.ival, _value(int(e.val)))
    elif isinstance(e.val, str):
      return _node(Tag.ival, _value(str(e.val)))
    else:
      raise ValueError(f"Invalid value {e}")
    pass
  elif isinstance(e, IAp):
    return _node(Tag.iap, _value((_value(iexpr2bin(e.func)),
                                 _value(iexpr2bin(e.arg)))))
  elif isinstance(e,ILam):
    return _node(Tag.ilam, _value((_value(e.name),
                                  _value(expr2bin(e.body)))))
  elif isinstance(e,IError):
    return _node(Tag.ierror, _value(str(e.msg)))
  else:
    raise ValueError(f"Invalid expression {e}")


def bin2iexpr(j:BIN)->IExpr:
  if j.tag == Tag.ival:
    if j.value.HasField('int64'):
      return IVal(int(j.value.int64))
    elif j.value.HasField('string'):
      return IVal(str(j.value.string))
    else:
      raise ValueError(f"Invalid value expression {j}")
  elif j.tag==Tag.ilam:
    return ILam(         j.value.tuple.v1.string,
                bin2expr(j.value.tuple.v2.node))
  elif j.tag==Tag.iap:
    return IAp(bin2iexpr(j.value.tuple.v1.node),
               bin2iexpr(j.value.tuple.v2.node))
  elif j.tag==Tag.ierror:
    return IError(j.value.string)
  else:
    raise ValueError(f"Invalid expression {_flat(j)}")


def imem2bin(m:IMem)->BIN:
  return \
    _node(Tag.imem, _value([
      _value((_value(k.name),
              _value(iexpr2bin(v)))) for k,v in m.dict.items()]))


def bin2imem(d:BIN)->IMem:
  assert d.tag == Tag.imem, f"Unexpected tag {d.tag}"
  return IMem({Ref(i.tuple.v1.string):bin2iexpr(i.tuple.v2.node)
               for i in d.value.list.list})


def ex2bin(e:Example)->BIN:
  return _node(Tag.example, _value((_value(imem2bin(e.inp)),
                                    _value((_value(expr2bin(e.expr)),
                                            _value(iexpr2bin(e.out)))))))

def bin2ex(e:BIN)->Example:
  assert e.tag==Tag.example
  return Example(bin2imem(e.value.tuple.v1.node),
                 bin2expr(e.value.tuple.v2.tuple.v1.node),
                 bin2iexpr(e.value.tuple.v2.tuple.v2.node))


from google.protobuf.internal.encoder import _VarintBytes    #type:ignore
from google.protobuf.internal.decoder import _DecodeVarint32 #type:ignore


def examples2fd(f)->Callable[[Example],int]:
  def _add(e:Example)->int:
    nwritten=0
    example = ex2bin(e)
    size = example.ByteSize()
    buf=_VarintBytes(size)
    f.write(buf)
    nwritten+=len(buf)
    buf=example.SerializeToString()
    f.write(buf)
    nwritten+=len(buf)
    return nwritten
  return _add


def fd2examples(f, chunk:int=256)->Callable[[],Example]:
  buf=bytearray()
  def _next()->Example:
    nonlocal buf
    buf+=f.read(chunk)
    msg_len,new_pos = _DecodeVarint32(buf,0)
    buf=buf[new_pos:]
    while len(buf)<msg_len:
      buf+=f.read(chunk)
    node=Node()
    node.ParseFromString(buf[:msg_len])
    buf=buf[msg_len:]
    return bin2ex(node)
  return _next

