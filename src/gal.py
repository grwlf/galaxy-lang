from os import environ
from os.path import join

from solution.lang import *




G=open(join(environ['SOLUTION_SOURCE'],'galaxy.txt'),'r').read()
M=Memory({})
load_program(M,G)
load_program(M,'''
  :9999 = ap ap galaxy nil ap ap cons 0 0
  :v0 = ap car :9999
  :v1 = ap cdr :9999
  ''')

# set_trace()
H={}
A=interp(M,mkref(':9999'),H)
print('A', pval(A[0]))

print('v0', pval(interp(M,mkref(':v0'),H)[0]))
print('v1', pval(interp(M,mkref(':v1'),H)[0]))
# print('v2', pval(interp(M,mkref(':v2'),H)[0]))
# print(pval(H[mkref('x0')]))

# set_trace()


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

