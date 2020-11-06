from galang.types import (Expr, Ref, TMap, Intrin, Lam, Val, Const, Ap, Let,
                          Mem, MethodName)
from galang.edsl import num, ref, let_, lam, ap, lam, intrin

from json import loads as json_loads, dumps as json_dumps

def t2json(e:Expr)->str:
  return json_dumps(t2dict(e))

def json2t(j:str)->Expr:
  return dict2t(json_loads(j))

def t2dict(e:Expr)->dict:
  if isinstance(e, Val):
    if isinstance(e.val, Const):
      return {'typ':'val', 'val':{'typ':'const', 'val':e.val.const}}
    elif isinstance(e.val, Ref):
      return {'typ':'val', 'val':{'typ':'ref', 'val':e.val.name}}
    else:
      raise ValueError(f"Invalid value expression {e}")
  elif isinstance(e, Lam):
    return {'typ':'lam', 'name':e.name, 'body':t2dict(e.body)}
  elif isinstance(e, Let):
    return {'typ':'let', 'ref':e.ref.name, 'expr':t2dict(e.expr), 'body':t2dict(e.body)}
  elif isinstance(e, Ap):
    return {'typ':'ap', 'func':t2dict(e.func), 'arg':t2dict(e.arg)}
  elif isinstance(e, Intrin):
    return {'typ':'intrin', 'name':e.name.val, 'args':[(n,t2dict(a)) for n,a in e.args.dict.items()]}
  else:
    raise ValueError(f"Invalid expression {e}")


def dict2t(j:dict)->Expr:
  typ = j['typ']
  if typ == 'val':
    vtyp = j['val']['typ']
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

