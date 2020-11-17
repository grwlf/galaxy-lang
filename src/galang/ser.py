from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin
from galang.interp import IMem, IExpr, IAp, ILam, IError, IVal

from typing import List
from json import loads as json_loads, dumps as json_dumps

def ts2json(es:List[Expr])->str:
  return json_dumps([t2dict(e) for e in es])

def json2ts(j:str)->List[Expr]:
  return [dict2t(x) for x in json_loads(j)]


def t2json(e:Expr)->str:
  return json_dumps(t2dict(e))

def json2t(j:str)->Expr:
  return dict2t(json_loads(j))

def t2dict(e:Expr)->dict:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return {'t':'val', 'val':{'t':'const', 'val':e.val.const}}
    elif isinstance(e.val, Ref):
      return {'t':'val', 'val':{'t':'ref', 'val':e.val.name}}
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return {'t':'lam', 'name':e.name, 'body':t2dict(e.body)}
  elif isinstance(e, Let):
    return {'t':'let', 'ref':e.ref.name, 'expr':t2dict(e.expr), 'body':t2dict(e.body)}
  elif isinstance(e, Ap):
    return {'t':'ap', 'func':t2dict(e.func), 'arg':t2dict(e.arg)}
  elif isinstance(e, Intrin):
    return {'t':'intrin', 'name':e.name.val, 'args':[(n,t2dict(a)) for n,a in e.args.dict.items()]}
  else:
    raise ValueError(f"Invalid expression {e}")


def dict2t(j:dict)->Expr:
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
    return lam(j['name'], lambda _: dict2t(j['body']))
  elif typ=='let':
    return let_(j['ref'], dict2t(j['expr']), lambda _: dict2t(j['body']))
  elif typ=='ap':
    return ap(dict2t(j['func']), dict2t(j['arg']))
  elif typ=='intrin':
    return intrin(MethodName(j['name']), [(k,dict2t(v)) for k,v in j['args']])
  else:
    raise ValueError(f"Invalid expression {j}")

def iexpr2dict(e:IExpr)->dict:
  if isinstance(e, IVal):
    if isinstance(e.val, int):
      return {'t':'ival', 'ival':{'t':'int', 'val':int(e.val)}}
    elif isinstance(e.val, str):
      return {'t':'ival', 'ival':{'t':'str', 'val':str(e.val)}}
    else:
      raise ValueError(f"Invalid value {e}")
    pass
  elif isinstance(e, IAp):
    return {'t':'iap', 'func':iexpr2dict(e.func), 'arg':iexpr2dict(e.arg)}
  elif isinstance(e,ILam):
    return {'t':'ilam', 'name':e.name, 'body':t2dict(e.body)}
  elif isinstance(e,IError):
    return {'t':'ierror', 'msg':e.msg}
  else:
    raise ValueError(f"Invalid expression {e}")

def dict2iexpr(j:dict)->IExpr:
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
    return ILam(j['name'], dict2t(j['body']))
  elif typ=='iap':
    return IAp(dict2iexpr(j['func']), dict2iexpr(j['arg']))
  elif typ=='ierror':
    return IError(j['msg'])
  else:
    raise ValueError(f"Invalid expression {j}")

def iexpr2json(e:IExpr):
  return json_dumps(iexpr2dict(e))

def json2iexpr(j:str):
  return dict2iexpr(json_loads(j))

