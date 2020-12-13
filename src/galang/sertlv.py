
from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin
from galang.interp import IMem, IExpr, IAp, ILam, IError, IVal, IMem


import galang.sertlv_pb2 as pb
from galang.sertlv_pb2 import Node, Value, Tuple as PBTuple, List as PBList

from typing import List, Any

TLV=Any

def _flat(v):
  return ' '.join(str(v).split())

def _node(tag, value):
  n=Node()
  n.tag = tag
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

def expr2tlv(e:Expr)->TLV:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return _node(pb.val, _value(_node(pb.const, _value(e.val.const))))
    elif isinstance(e.val, Ref):
      return _node(pb.val, _value(_node(pb.ref, _value(e.val.name))))
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return _node(pb.lam, _value((_value(e.name),
                                   _value(expr2tlv(e.body)))))
  elif isinstance(e, Let):
    return _node(pb.let, _value((_value(e.ref.name),
                                   _value((_value(expr2tlv(e.expr)),
                                           _value(expr2tlv(e.body)))))))
  elif isinstance(e, Ap):
    return _node(pb.ap, _value((_value(expr2tlv(e.func)),
                                  _value(expr2tlv(e.arg)))))
  elif isinstance(e, Intrin):
    return _node(pb.intrin, _value((_value(e.name.val),
                                      _value([_value((_value(n),
                                                      _value(expr2tlv(a))))
                                             for n,a in e.args.dict.items()]))))
  else:
    raise ValueError(f"Invalid expression {e}")

def tlv2expr(j:TLV)->Expr:
  typ = j.tag
  if typ == pb.val:
    vtyp = j.value.node.tag
    if vtyp == pb.const:
      return num(j.value.node.value.int64)
    elif vtyp == pb.ref:
      return ref(j.value.node.value.string)
    else:
      raise ValueError(f"Invalid value expression {_flat(j)}")
  elif typ==pb.lam:
    return lam(j.value.tuple.v1.string, lambda _: tlv2expr(j.value.tuple.v2.node))
  elif typ==pb.let:
    return let_(j.value.tuple.v1.string,
                          tlv2expr(j.value.tuple.v2.tuple.v1.node),
                lambda _: tlv2expr(j.value.tuple.v2.tuple.v2.node))
  elif typ==pb.ap:
    return ap(tlv2expr(j.value.tuple.v1.node),
              tlv2expr(j.value.tuple.v2.node))
  elif typ==pb.intrin:
    return intrin(MethodName(j.value.tuple.v1.string),
                  [(         v.tuple.v1.string,
                    tlv2expr(v.tuple.v2.node)) for v in j.value.tuple.v2.list.list])
  else:
    raise ValueError(f"Invalid expression {_flat(j)}")


def iexpr2tlv(e:IExpr)->dict:
  if isinstance(e, IVal):
    if isinstance(e.val, int):
      return _node(pb.ival, _value(int(e.val)))
    elif isinstance(e.val, str):
      return _node(pb.ival, _value(str(e.val)))
    else:
      raise ValueError(f"Invalid value {e}")
    pass
  elif isinstance(e, IAp):
    return _node(pb.iap, _value((_value(iexpr2tlv(e.func)),
                                 _value(iexpr2tlv(e.arg)))))
  elif isinstance(e,ILam):
    return _node(pb.ilam, _value((_value(e.name),
                                  _value(expr2tlv(e.body)))))
  elif isinstance(e,IError):
    return _node(pb.ierror, _value(str(e.msg)))
  else:
    raise ValueError(f"Invalid expression {e}")


def tlv2iexpr(j:TLV)->IExpr:
  if j.tag == pb.ival:
    if j.value.HasField('int64'):
      return IVal(int(j.value.int64))
    elif j.value.HasField('string'):
      return IVal(str(j.value.string))
    else:
      raise ValueError(f"Invalid value expression {j}")
  elif j.tag==pb.ilam:
    return ILam(         j.value.tuple.v1.string,
                tlv2expr(j.value.tuple.v2.node))
  elif j.tag==pb.iap:
    return IAp(tlv2iexpr(j.value.tuple.v1.node),
               tlv2iexpr(j.value.tuple.v2.node))
  elif j.tag==pb.ierror:
    return IError(j.value.string)
  else:
    raise ValueError(f"Invalid expression {_flat(j)}")

