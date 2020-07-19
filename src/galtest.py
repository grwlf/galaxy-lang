from os import environ
from os.path import join

from solution.lang import *

# prog_test('''
#   :1 = :2
#   :2 = ap ap add :1 1
#   ''', '33')


# prog_test('''
#   :1 = 32
#   :2 = ap ap add :1 1
#   ''', '33')

# run_test('isnil', '''
#   ap isnil nil   =   t
#   ap isnil ap ap cons 33 44   =   f
#   ''')

run_test('add', '''
  #ap (ap ap add 1 1) 1 = 2
  ap ap ap add 1 1 1 != 2

  # ap (ap add (ap (ap add 1) 2)) 3  = 5
  ap ap add ap ap add 1 2 3 = 6

  ap ap add 1 2   =   3
  ap ap add 2 1   =   3
  ap ap add 0 1   =   1
  ap ap add 2 3   =   5
  ap ap add 3 5   =   8
  ''')


run_test('eq', '''
  ap ap eq 33 33   =   t
  ap ap eq 0 -2   =   f
  ap ap eq 0 -1   =   f
  ap ap eq 0 0   =   t
  ap ap eq 0 1   =   f
  ap ap eq 0 2   =   f

  ap ap eq 1 -1   =   f
  ap ap eq 1 0   =   f
  ap ap eq 1 1   =   t
  ap ap eq 1 2   =   f
  ap ap eq 1 3   =   f

  ap ap eq 2 0   =   f
  ap ap eq 2 1   =   f
  ap ap eq 2 2   =   t
  ap ap eq 2 3   =   f
  ap ap eq 2 4   =   f

  ap ap eq 19 20   =   f
  ap ap eq 20 20   =   t
  ap ap eq 21 20   =   f

  ap ap eq -19 -20   =   f
  ap ap eq -20 -20   =   t
  ap ap eq -21 -20   =   f
  ''')


run_test('mul', '''
    ap ap mul 4 2   =   8
    ap ap mul 3 4   =   12
    ap ap mul 3 -2   =   -6
    ''')

run_test('div', '''
  ap ap div 4 2   =   2
  ap ap div 4 3   =   1
  ap ap div 4 4   =   1
  ap ap div 4 5   =   0
  ap ap div 5 2   =   2
  ap ap div 6 -2   =   -3
  ap ap div 5 -3   =   -1
  ap ap div -5 3   =   -1
  ap ap div -5 -3   =   1
  ''')

run_test('neg', '''
  ap neg 0   =   0
  ap neg 1   =   -1
  ap neg -1   =   1
  ap neg 2   =   -2
  ap neg -2   =   2
  ''')

run_test('ap', '''
  ap inc ap inc 0   =   2
  ap inc ap inc ap inc 0   =   3
  ap ap add ap ap add 2 3 4   =   9
  ap ap add 2 ap ap add 3 4   =   9
  ap ap add ap ap mul 2 3 4   =   10
  ap ap mul 2 ap ap add 3 4   =   14
  ap inc ap dec 44   =   44
  ap dec ap inc 33   =   33
  ap dec ap ap add 33 1   =   33
  ''')

run_test('c', '''
  ap ap ap c add 1 2   =   3
  ''')

run_test('s', '''
  ap ap ap s add inc 1   =   3
  ap ap ap s mul ap add 1 6   =   42
  ''')

run_test('b', '''
  ap ap ap b inc dec 33   =   33
  ''')

## ap pwr2 0   =   ap ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 (3.1.2 . ap 3 (b 0.5 1 2))




## FIXME: pwr2 requires untyped interpetation

run_test('pwr2', '''
  # pwr2   =   ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1
  ap pwr2 1   =   2

  # ap pwr2 0   =   ap ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1 0
  #
  # ap pwr2 0   =   ap ap ap ap c ap eq 0 1 0 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 0

  # ap pwr2 0   =   ap ap ap ap eq 0 0 1 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 0
  # ap pwr2 0   =   ap ap t 1 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 0
  ap pwr2 0   =   1

  # ap pwr2 1   =   ap ap mul 2 ap ap ap ap eq 0 ap ap add -1 1 1 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 ap ap add -1 1
  # ap pwr2 1   =   ap ap mul 2 ap ap ap ap eq 0 0 1 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 ap ap add -1 1
  # ap pwr2 1   =   ap ap mul 2 ap ap t 1 ap ap ap b ap mul 2 ap ap b pwr2 ap add -1 ap ap add -1 1
  ap pwr2 1   =   ap ap mul 2 1
  ''')

run_test('i', '''
  ap i 343   =   343
  ap i 1   =   1

  # Actually it works
  # ap i i   =   i
  # ap i add   =   add
  # ap i ap add 1   =   ap add 1
  ''')

run_test('car', '''
  ap car ap ap cons 33 42   =   33
  ap car ap ap cons 33 42   =   33
  # ap car i   =   ap i t
  ''')

run_test('cdr', '''
  ap cdr ap ap cons 33 nil   =   nil
  ''')

run_test('cons', '''
  # ap ap ap cons x0 x1 x2   =   ap ap x2 x0 x1
  ap car ap ap cons 33 ap ap cons 42 ap ap cons 666 nil = 33
  ''')

run_test('nil', '''
  # ap nil 33   =   t
  ''')

run_test('isnil', '''
  ap isnil nil   =   t
  ap isnil ap ap cons 33 44   =   f
  ''')

run_test('if0', '''
  ap ap ap if0 0 33 42   =   33
  ap ap ap if0 1 33 42   =   42
  ''')




assert nbits_mod4(0)==0
assert nbits_mod4(1)==1
assert nbits_mod4(7)==1
assert nbits_mod4(15)==1
assert nbits_mod4(16)==2, f'{nbits_mod4(16)}'
assert nbits_mod4(255)==2
assert nbits_mod4(256)==3


def modem_test(x:Val):
  print(f"Testing modem on {x}")
  s=mod_val(x).body
  x2,sz=dem_val(s)
  assert x==x2, f"{x} != {x2}"
  assert sz==len(s)

modem_test(mknil())
modem_test(mkint(0))
modem_test(mkint(-1))
modem_test(mkint(-257))
modem_test(mkint(1024))
modem_test(mktuple(mkint(0),mknil()))
modem_test(mktuple(mkint(1),mktuple(mkint(2),mktuple(mkint(3),mknil()))))
modem_test(mktuple(mkint(1),mkint(2)))


# V=run_program(':33', interp_program('''
#   :0 = cons
#   :1 = 22
#   :2 = 33
#   :33 = ap ap :0 :1 :2
#   '''))
#print(V)





# G=open(join(environ['SOLUTION_SOURCE'],'galaxy.txt'),'r').read()
# M=Memory({})
# load_program(G,M)
# load_program('''
#   :9999 = ap ap galaxy nil ap ap cons 0 0
#   ''',M)

# set_trace()
# interp(M,mkref(':9999'))

## print(P)


