import altair as alt
import pandas as pd
from altair_saver import save as altair_save
from os.path import isfile
from shutil import rmtree

def test_altair():
  df=pd.DataFrame({'x':[1,2,3], 'y':[1,4,9]})
  c=alt.Chart(df).mark_line().encode(x='x', y='y')
  rmtree('/tmp/plot.png', ignore_errors=True)
  altair_save(c,'/tmp/plot.png')
  assert isfile('/tmp/plot.png')
