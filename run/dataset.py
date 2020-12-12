#!/usr/bin/env python3

from typing import List, Optional, Any, Dict, Iterable, Callable

from galang.interp import interp, IVal, IExpr, IMem
from galang.edsl import let_, let, num, intrin, call, ref, num, lam, ap
from galang.domain.arith import lib as lib_arith
from galang.gen import genexpr, permute, WLib, mkwlib
from galang.types import MethodName, TMap, Dict, mkmap, Ref, Mem, Expr
from galang.utils import refs, print_expr, gather

from pylightnix import realize, instantiate, store_initialize
from galang.stages.all import stage_dataset


store_initialize()
