#! /usr/bin/env nix-shell
#! nix-shell -i /bin/sh -p pkgs.jdk pkgs.maven

set -e -x

openapi-generator-cli generate \
  -i https://icfpc2020-api.testkontur.ru/swagger/api/swagger.json \
  -g python -o `pwd`/3rdparty/openapi

rm -rf `pwd`/src/openapi_client || true
cp -r `pwd`/3rdparty/openapi/openapi_client `pwd`/src/openapi_client
