#{ pkgs ?  import ./lib/nixpkgs {}
{ pkgs ?  import <nixpkgs> {}
, stdenv ? pkgs.stdenv
} :
let

  self = pkgs.python37Packages;
  inherit (pkgs) fetchgit;
  inherit (self) buildPythonPackage fetchPypi;

  pyls = self.python-language-server.override { providers=["pycodestyle" "pyflakes"]; };
  pyls-mypy = self.pyls-mypy.override { python-language-server=pyls; };

  be = pkgs.mkShell {
    name = "pythonshell";
    buildInputs =
    ( with pkgs;
      with self;
    [
      ipython
      pyls-mypy
      pyls

      numpy
      pandas
    ]);

    shellHook = with pkgs; ''
      if test -f ./env.sh ; then
        . ./env.sh
      fi
    '';
  };

in
  be
