from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName, IMem, IExpr, IAp, ILam, IError, IVal,
                          IMem)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin

from typing import List
from json import loads as json_loads, dumps as json_dumps

def exprs2json(es:List[Expr])->list:
  return [expr2json(e) for e in es]
def list2exprs(l:list)->List[Expr]:
  return [json2expr(d) for d in l]

def exprs2jstr(es:List[Expr])->str:
  return json_dumps(exprs2json(es))
def jstr2exprs(j:str)->List[Expr]:
  return list2exprs(json_loads(j))


def expr2jstr(e:Expr)->str:
  return json_dumps(expr2json(e))

def jstr2expr(j:str)->Expr:
  return json2expr(json_loads(j))

def expr2json(e:Expr)->dict:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return {'t':'val', 'val':{'t':'const', 'val':e.val.const}}
    elif isinstance(e.val, Ref):
      return {'t':'val', 'val':{'t':'ref', 'val':e.val.name}}
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return {'t':'lam', 'name':e.name, 'body':expr2json(e.body)}
  elif isinstance(e, Let):
    return {'t':'let', 'ref':e.ref.name, 'expr':expr2json(e.expr), 'body':expr2json(e.body)}
  elif isinstance(e, Ap):
    return {'t':'ap', 'func':expr2json(e.func), 'arg':expr2json(e.arg)}
  elif isinstance(e, Intrin):
    return {'t':'intrin', 'name':e.name.val, 'args':[(n,expr2json(a)) for n,a in e.args.dict.items()]}
  else:
    raise ValueError(f"Invalid expression {e}")


def json2expr(j:dict)->Expr:
  typ = j['t']
  if typ == 'val':
    vtyp = j['val']['t']
    if vtyp == 'const':
      return num(j['val']['val'])
    elif vtyp == 'ref':
      return ref(j['val']['val'])
    else:
      raise ValueError(f"Invalid value expression {j}")
  elif typ=='lam':
    return lam(j['name'], lambda _: json2expr(j['body']))
  elif typ=='let':
    return let_(j['ref'], json2expr(j['expr']), lambda _: json2expr(j['body']))
  elif typ=='ap':
    return ap(json2expr(j['func']), json2expr(j['arg']))
  elif typ=='intrin':
    return intrin(MethodName(j['name']), [(k,json2expr(v)) for k,v in j['args']])
  else:
    raise ValueError(f"Invalid expression {j}")

def iexpr2json(e:IExpr)->dict:
  if isinstance(e, IVal):
    if isinstance(e.val, int):
      return {'t':'ival', 'ival':{'t':'int', 'val':int(e.val)}}
    elif isinstance(e.val, str):
      return {'t':'ival', 'ival':{'t':'str', 'val':str(e.val)}}
    else:
      raise ValueError(f"Invalid value {e}")
    pass
  elif isinstance(e, IAp):
    return {'t':'iap', 'func':iexpr2json(e.func), 'arg':iexpr2json(e.arg)}
  elif isinstance(e,ILam):
    return {'t':'ilam', 'name':e.name, 'body':expr2json(e.body)}
  elif isinstance(e,IError):
    return {'t':'ierror', 'msg':e.msg}
  else:
    raise ValueError(f"Invalid expression {e}")

def json2iexpr(j:dict)->IExpr:
  typ = j['t']
  if typ == 'ival':
    vtyp = j['ival']['t']
    if vtyp == 'int':
      return IVal(int(j['ival']['val']))
    elif vtyp == 'str':
      return IVal(str(j['ival']['val']))
    else:
      raise ValueError(f"Invalid value expression {j}")
  elif typ=='ilam':
    return ILam(j['name'], json2expr(j['body']))
  elif typ=='iap':
    return IAp(json2iexpr(j['func']), json2iexpr(j['arg']))
  elif typ=='ierror':
    return IError(j['msg'])
  else:
    raise ValueError(f"Invalid expression {j}")

def iexpr2jstr(e:IExpr)->str:
  return json_dumps(iexpr2json(e))

def jstr2iexpr(j:str)->IExpr:
  return json2iexpr(json_loads(j))


def imem2json(m:IMem)->dict:
  return {k.name:iexpr2json(v) for k,v in m.dict.items()}
def json2imem(d:dict)->IMem:
  return IMem({Ref(k):json2iexpr(v) for k,v in d.items()})
def imem2jstr(m:IMem)->str:
  return json_dumps(imem2json(m))
def jstr2imem(j:str)->IMem:
  return json2imem(json_loads(j))


