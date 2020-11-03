#{ pkgs ?  import ./lib/nixpkgs {}
{ pkgs ?  import <nixpkgs> {}
, stdenv ? pkgs.stdenv
} :
let

  self = pkgs.python37Packages;
  inherit (pkgs) fetchgit fetchFromGitHub;
  inherit (self) buildPythonPackage fetchPypi;

  pyls = self.python-language-server.override { providers=["pycodestyle"]; };
  pyls-mypy = self.pyls-mypy.override { python-language-server=pyls; };

  frozenordereddict = buildPythonPackage rec {
    name = "frozenordereddict";
    src = fetchgit {
      url = "https://github.com/wsmith323/frozenordereddict";
      rev = "8837a7e2b55cf8531793b0ec5ad40d56c500ec0f";
      sha256 = "sha256:0qr88gg5bsw30dca8p7a3dzqaimdwball0mmlwvlcr6mw6jn3mcc";
    };
    postFixup = ''
      for dst in `find $out -path '*frozenordereddict/__init__.py'` ; do
        sed -i 's/from collections import Mapping/from collections.abc import Mapping/g' $dst
        for src in `find $src -path '*frozenordereddict/VERSION.txt'` ; do
          cp $src `dirname $dst`
        done
      done
    '';
  };

  parsec = buildPythonPackage rec {
    name = "parsec";
    src = fetchgit {
      url = "https://github.com/sighingnow/parsec.py";
      rev = "706ee10cd4a426dbbebbe2246a23172aebb5691f";
      sha256 = "sha256:1dlrlvb4b9y1lmbqfsmzg854aap94gdsi63mcy3iqqdfir3zr8ym";
    };
  };

  be = pkgs.mkShell {
    name = "pythonshell";
    buildInputs =
    [
      pyls-mypy
      # pyls
    ] ++
    ( with pkgs;
      with self;
    [
      ipython
      # yapf
      # rope
      # pylint
      # pydocstyle
      # autopep8
      # pyflakes

      numpy
      pandas
      parsec
      pytest-mypy
      ipdb
      hypothesis

      immutables
      frozendict
      frozenordereddict

      pytorch
    ]);

    shellHook = with pkgs; ''
      if test -f ./env.sh ; then
        . ./env.sh
      fi
      # export MYPYPATH=${self.immutables}/lib/python3.7/site-packages:`pwd`/src:`pwd`/tests
    '';
  };

in
  be
