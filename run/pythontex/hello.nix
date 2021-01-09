{ pkgs? import <nixpkgs> {}
, stdenv ? pkgs.stdenv
}:

let
  version = "2.10";
  url = "mirror://gnu/hello/hello-${version}.tar.gz";
  sha256 = "0ssi1wpaf7plaswqqjwigppsg5fyh99vdlb9kzl7c9lng89ndq1i";
in
with pkgs;
stdenv.mkDerivation rec {
  name = "hello";
  src = fetchurl { inherit url sha256; };

  buildInputs = [ gnutar ];

  buildCommand = ''
    tar -xzf $src
    cd hello-2.10
    ./configure --prefix=$out
    make
    make install
  '';
}
