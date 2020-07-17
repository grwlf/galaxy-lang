from typing import List, Optional, Any, Callable, Dict
from dataclasses import dataclass




@dataclass
class Term:
  name:str
  nargs:int



inc=Term('inc',1)
dec=Term('dec',1)
sum=Term('sum',2)
mul=Term('mul',2)
div=Term('dic',2)
eq=Term('eq',2)
lt=Term('lt',2)
mod=Term('mod',1) # has a list version
dem=Term('dem',1)
send=Term('send',1)
neg=Term('neg',1)
ap=Term('ap',2)
#S
#C
#B
#K(True)
#False
pwr2=Term('pwr2',2)
#I
cons=Term('cons',2)
car=Term('car',2)
cdr=Term('cdr',2)
nil=Term('nil',1)
isnil=Term('isnil',1)
draw=Term('draw',1) # [x,y]->img
checkerboard=Term('checkerboard',2)
multipledraw=Term('multipledraw',1) # [x]->img???
if0=Term('if0',3)


