Galaxy-lang
===========

Several experiments on
[#program-synthesis](https://paperswithcode.com/task/program-synthesis)
reside in this place.

* [src/galang/gen.py](./src/galang/gen.py) contains simplified implementation of
[TF-Coder's Synthesis Algorithm](https://paperswithcode.com/paper/tf-coder-program-synthesis-for-tensor)


Usage
-----

0. Install Nix package manager
1. Type `nix-shell` to enter development shell
2. Compile Protobuf wrappers `protoc src/galang/serbin.proto --python_out=.`
3. Run `./ipython.sh` helper to run IPython
4. ... (work is in progress)


References
----------

**Papers**

* [TF-Coder at OpenReview](https://openreview.net/forum?id=nJ5Ij53umw2)

**Python**

* [Protocol buffers docs, proto2](https://developers.google.com/protocol-buffers/)
* [Protocol buffers docs, proto3](https://developers.google.com/protocol-buffers/docs/proto3)
* https://www.datadoghq.com/blog/engineering/protobuf-parsing-in-python/
* [Struct](https://docs.python.org/3/library/struct.html)

**Pandas**

* [GroupBy API Reference](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html)
* [GroupBy User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html)

**Altair**

* [Altair gallery](https://altair-viz.github.io/gallery/)
* [Altair common customization](https://altair-viz.github.io/user_guide/customization.html)

**Literate programming**

* [Lepton](https://www.math.univ-paris13.fr/~lithiao/ResearchLepton/Lepton.html)
* [Pythontex](https://github.com/gpoore/pythontex)

