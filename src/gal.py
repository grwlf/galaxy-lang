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

def geval(M,heap,line,hint='')->Tuple[Ref,Val]:
  r=newref()
  heap[r]=load_expr(parse_expr(line))
  interp(M,r,heap)
  v=unref(M,heap,r)
  print(f"{pval(v)} # {hint}" if len(hint)>0 else pval(v) )
  return r,v

# def scanlist2d(M,h,rimg)->List[Tuple[int,int]]:
#   acc=[]
#   isnil=mkint(0)
#   def _eval(line,hint='')->Tuple[Ref,Val]:
#     return geval(M,h,line,hint)
#   while asint(isnil)==0:
#     rpoint,point=_eval(f"ap car {rimg.to}", "point")
#     rx,x=_eval(f"ap car {rpoint.to}", "x")
#     ry,y=_eval(f"ap cdr {rpoint.to}", "y")
#     acc.append((x,y))
#     rimg,img=_eval(f"ap cdr {rimg.to}", "next point")
#     risnil,isnil=_eval(f"ap ap ap isnil {rimg.to} 1 0", "is nil?")
#   return acc

def maplist(M,h,rimg,fn)->List[Any]:
  acc=[]
  isnil=mkint(0)
  def _eval(line,hint='')->Tuple[Ref,Val]:
    return geval(M,h,line,hint)
  while asint(isnil)==0:
    rpoint,point=_eval(f"ap car {rimg.to}", "point")
    item=fn(M,h,rpoint)
    acc.append(item)
    rimg,img=_eval(f"ap cdr {rimg.to}", "next point")
    risnil,isnil=_eval(f"ap ap ap isnil {rimg.to} 1 0", "is nil?")
  return acc

def unpoint(M,h,rpoint)->Tuple[int,int]:
  rx,x=geval(M,h,f"ap car {rpoint.to}", "x")
  ry,y=geval(M,h,f"ap cdr {rpoint.to}", "y")
  return (asint(x),asint(y))

def unimg(M,heap,rimg):
  img=maplist(M,heap,rimg,unpoint)
  # showimg(img)
  return img

from solution.gui import showimg

def draw(M:Memory):
  """ r should point to list """
  heap={}
  rgal=mkref(':9999')
  interp(M,rgal,heap)

  print('Galaxy:')
  print(pval(heap[rgal]))

  def _eval(line,hint='')->Tuple[Ref,Val]:
    return geval(M,heap,line,hint)

  rg1,g1=_eval(f"ap car {rgal.to}")
  rg2,g2=_eval(f"ap car ap cdr {rgal.to}")
  rg3,g3=_eval(f"ap car ap cdr ap cdr {rgal.to}", 'list of list of points')

  r=rg3

  imgs=maplist(M,heap,r,unimg)
  return imgs

  # while True:
  #   rimg,img=_eval(f"ap car {r.to}", "list of points")

  #   img=maplist(M,heap,rimg,unpoint)
  #   return img
  #   # showimg(img)

  #   set_trace()



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
