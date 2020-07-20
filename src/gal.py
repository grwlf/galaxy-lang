from os import environ
from os.path import join

from solution.lang import *




G=open(join(environ['SOLUTION_SOURCE'],'galaxy.txt'),'r').read()
M=Memory({})
load_program(M,G)
load_program(M,'''
  :9999 = ap ap galaxy nil ap ap cons 0 0
  ''')

# xxx = ap ap galaxy :v1 ap ap cons 0 nil
# set_trace()
# print('A', pval(A[0]))

# print('v0', pval(interp(M,mkref(':v0'),H)[0]))
# print('v1', pval(interp(M,mkref(':v2'),H)[0]))
# print('v2', pval(interp(M,mkref(':v2'),H)[0]))
# print('xxx', pval(interp(M,mkref('xxx'),H)[0]))
# print('v2', pval(interp(M,mkref(':v2'),H)[0]))
# print('v3', pval(interp(M,mkref(':v3'),H)[0]))
# print(pval(H[mkref('x0')]))

# set_trace()

def draw(M:Memory):
  """ r should point to list """
  heap={}
  rgal=mkref(':9999')
  interp(M,rgal,heap)

  print('Galaxy:')
  print(pval(heap[rgal]))

  def _eval(line,hint='')->Tuple[Ref,Val]:
    r=newref()
    heap[r]=load_expr(parse_expr(line))
    interp(M,r,heap)
    v=unref(M,heap,r)
    print(f"{pval(v)} # {hint}" if len(hint)>0 else pval(v) )
    return r,v

  rg1,g1=_eval(f"ap car {rgal.to}")
  rg2,g2=_eval(f"ap car ap cdr {rgal.to}")
  rg3,g3=_eval(f"ap car ap cdr ap cdr {rgal.to}", 'list of list of points')

  r=rg3
  while True:
    set_trace()
    rimg,img=_eval(f"ap car {r.to}", "first list of points")
    rpoint,point=_eval(f"ap car {rimg.to}", "point")
    rx,x=_eval(f"ap car {rpoint.to}", "x")
    ry,y=_eval(f"ap car ap cdr {rpoint.to}", "y")

    print(pval(heap[relem]))

    rnext=newref()
    heap[rnext]=mkap(cdr, mkvref(r))
    interp(M,rnext,heap)
    print(pval(heap[rnext]))

    r=heap[rnext]


# G=open(join(environ['SOLUTION_SOURCE'],'galaxy.txt'),'r').read()
# M=Memory({})
# load_program(M,G)
# load_program(M,'''
#   :9999 = galaxy
#   ''')

# # set_trace()
# H={}
# A=interp(M,mkref(':9999'),H)
# print('A', pval(A[0]))

# print('v0', pval(interp(M,mkref(':v0'),H)[0]))
# print('v1', pval(interp(M,mkref(':v1'),H)[0]))
# print('v2', pval(interp(M,mkref(':v2'),H)[0]))
# print('v3', pval(interp(M,mkref(':v3'),H)[0]))
# print('v4', pval(interp(M,mkref(':v4'),H)[0]))
# print('v5', pval(interp(M,mkref(':v5'),H)[0]))

# print('v3', pval(interp(M,mkref(':v2'),H)[0]))
# print('z', pval(interp(M,mkref(':z'),H)[0]))

if __name__=='__main__':
  draw(M)
