from tempfile import TemporaryDirectory
from shutil import copytree
from os import getcwd, chdir, system
from os.path import join
from pylightnix import (Manager, DRef, RRef, Config, RefPath, mkconfig, Path,
                        Build, build_cattrs, build_outpath, mkdrv,
                        build_wrapper, match_latest, dirrw, mklens,
                        instantiate_inplace, realize_inplace, fetchurl)

hello_version = '2.10'

hello_src:DRef = \
  instantiate_inplace(
    fetchurl,
    name='hello-src',
    url=f'http://ftp.gnu.org/gnu/hello/hello-{hello_version}.tar.gz',
    sha256='31e066137a962676e89f69d1b65382de95a7ef7d914b8cb956f41ea72e0f516b')

def stage_hello(m:Manager)->DRef:
  def _config()->Config:
    name:str = 'hello-bin'
    src:RefPath = [hello_src, f'hello-{hello_version}']
    return locals()
  def _make(b:Build)->None:
    o:Path = build_outpath(b)
    with TemporaryDirectory() as tmp:
      copytree(mklens(b).src.syspath,join(tmp,'src'))
      dirrw(Path(join(tmp,'src')))
      cwd = getcwd()
      try:
        chdir(join(tmp,'src'))
        system('./configure --prefix=/usr')
        system('make')
        system(f'make install DESTDIR={o}')
      finally:
        chdir(cwd)
  return mkdrv(m, mkconfig(_config()), match_latest(), build_wrapper(_make))


hello_rref:RRef = realize_inplace(instantiate_inplace(stage_hello))

print(hello_rref)

