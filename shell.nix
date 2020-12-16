#{ pkgs ?  import ./lib/nixpkgs {}
# { pkgs ?  import <nixpkgs> {}
{ pkgs ?  import ./3rdparty/nixpkgs {}
, stdenv ? pkgs.stdenv
} :
let

  self = pkgs.python37Packages;
  inherit (pkgs) fetchurl fetchgit fetchFromGitHub;
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

  altair-data-server = buildPythonPackage rec {
    name = "altair-data-server";
    src = fetchPypi {
      version = "0.4.1";
      pname = "altair_data_server";
      sha256 = "sha256:0azbkakgbjwxvkfsvdcw2vnpjn44ffwrqwsqzhh80rxjiaj0b4mk";
    };
    buildInputs = with self; [ altair portpicker tornado jinja2 pytest ];
  };

  altair-viewer = buildPythonPackage rec {
    name = "altair-viewer";
    src = fetchPypi {
      version = "0.3.0";
      pname = "altair_viewer";
      sha256 = "sha256:0fa4ab233jbx11jfim35qys9yz769pdhkmfrvliyfnvwdggdnr19";
    };
    buildInputs = with self; [ altair altair-data-server portpicker tornado
                               jinja2 pytest ipython ];
  };

  altair-saver = buildPythonPackage rec {
    name = "altair-saver";
    src = fetchPypi {
      version = "0.5.0";
      pname = "altair_saver";
      sha256 = "sha256:15c7p23m8497jpvabg49bd858nsip31lv408n4fs2fwfhvvbr660";
    };
    # preConfigure = ''
    #   sed -i 's/selenium//g' requirements.txt
    # '';
    propagatedBuildInputs = with self; [ altair-viewer pkgs.nodejs altair-data-server
      altair portpicker tornado jinja2 pytest selenium
      pillow pypdf2];
  };

  i686_NIX_GCC = pkgs.pkgsi686Linux.callPackage ({gcc}: gcc) {};

  ld32 =
    if stdenv.hostPlatform.system == "x86_64-linux" then "${stdenv.cc}/nix-support/dynamic-linker-m32"
    else if stdenv.hostPlatform.system == "i686-linux" then "${stdenv.cc}/nix-support/dynamic-linker"
    else throw "Unsupported platform for PlayOnLinux: ${stdenv.hostPlatform.system}";

  lepton = stdenv.mkDerivation rec {
    name = "lepton";
    src = fetchurl {
      inherit name;
      url = "http://www.math.univ-paris13.fr/~lithiao/ResearchLepton/send.php?file=lepton";
      sha256 = "sha256:1w2s1y5dzjxirasxb8y24dy03ag6rzasbm4vijldj1xhjs088zcd";
    };
    buildCommand = ''
      set -x
      mkdir -pv $out/bin
      cp -v $src $out/bin/lepton
      chmod 755 $out/bin/*
      patchelf --interpreter "$(cat ${i686_NIX_GCC}/nix-support/dynamic-linker)" $out/bin/lepton
    '';
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
      lepton
      ocaml  # to test lepton
      strace
      gdb

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

      protobuf
      # mypy-protobuf Doesn't work
      altair
      altair-data-server
      altair-viewer
      altair-saver

      nodePackages.vega-lite
      nodePackages.vega-cli
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
