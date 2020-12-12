
from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin
from galang.interp import IMem, IExpr, IAp, ILam, IError, IVal, IMem


import galang.sertlv_pb2 as pb
from galang.sertlv_pb2 import Node, Value, Tuple, List as PBList

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
  t=Tuple()
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
      return _node(Node.val, _value(_node(Node.const, _value(e.val.const))))
    elif isinstance(e.val, Ref):
      return _node(Node.val, _value(_node(Node.ref, _value(e.val.name))))
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return _node(Node.lam, _value((_value(e.name),
                                   _value(expr2tlv(e.body)))))
  elif isinstance(e, Let):
    return _node(Node.let, _value((_value(e.ref.name),
                                   _value((_value(expr2tlv(e.expr)),
                                           _value(expr2tlv(e.body)))))))
  elif isinstance(e, Ap):
    return _node(Node.ap, _value((_value(expr2tlv(e.func)),
                                  _value(expr2tlv(e.arg)))))
  elif isinstance(e, Intrin):
    return _node(Node.intrin, _value((_value(e.name.val),
                                      _value([_value((_value(n),
                                                      _value(expr2tlv(a))))
                                             for n,a in e.args.dict.items()]))))
  else:
    raise ValueError(f"Invalid expression {e}")

def tlv2expr(j:TLV)->Expr:
  typ = j.tag
  if typ == Node.val:
    vtyp = j.value.node.tag
    if vtyp == Node.const:
      return num(j.value.node.value.int64)
    elif vtyp == Node.ref:
      return ref(j.value.node.value.string)
    else:
      raise ValueError(f"Invalid value expression {_flat(j)}")
  elif typ==Node.lam:
    return lam(j.value.tuple.v1.string, lambda _: tlv2expr(j.value.tuple.v2.node))
  elif typ==Node.let:
    return let_(j.value.tuple.v1.string,
                          tlv2expr(j.value.tuple.v2.tuple.v1.node),
                lambda _: tlv2expr(j.value.tuple.v2.tuple.v2.node))
  elif typ==Node.ap:
    return ap(tlv2expr(j.value.tuple.v1.node),
              tlv2expr(j.value.tuple.v2.node))
  elif typ==Node.intrin:
    return intrin(MethodName(j.value.tuple.v1.string),
                           [(v.tuple.v1.string,
                    tlv2expr(v.tuple.v2.node)) for v in j.value.tuple.v2.list.list])
  else:
    raise ValueError(f"Invalid expression {_flat(j)}")



