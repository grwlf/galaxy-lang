Galaxy-lang
===========

Several experiments on
[#program-synthesis](https://paperswithcode.com/task/program-synthesis)
reside in this place.

* [src/galang/gen.py](./src/galang/gen.py) contains simplified implementation of
[TF-Coder's Synthesis Algorithm](https://paperswithcode.com/paper/tf-coder-program-synthesis-for-tensor)


Usage
-----

1. Install [Nix package manager](https://github.com/NixOS/nix)
2. Clone this repo and it's submodules:
   `git clone --recursive https://github.com/grwlf/galaxy-lang && cd galaxy-lang`
3. Type `nix-shell` to build/fetch dependencies and enter development shell.
4. Compile Protobuf wrappers `protoc src/galang/serbin.proto --python_out=.`
5. Run `./ipython.sh` helper to enter IPython shell.
6. ... (work is in progress)


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

**LaTeX**

* [Algorithms](https://shantoroy.com/latex/how-to-write-algorithm-in-latex/)
* [UtilSnips](https://github.com/SirVer/ultisnips)
* [Vim+LaTex guide (in Russian)](https://m.habr.com/ru/post/445066/)
* Literate programming:
  - [Lepton](https://www.math.univ-paris13.fr/~lithiao/ResearchLepton/Lepton.html)
    + [Lepton Sources](https://github.com/slithiaote/lepton)
  - [Pythontex](https://github.com/gpoore/pythontex)

**Math**

* [Mean and Variance](https://online.stat.psu.edu/stat414/lesson/24/24.3)
* [Sample Mean and Variance](https://online.stat.psu.edu/stat414/lesson/26/26.3)

Related issues
--------------

* https://github.com/altair-viz/altair/issues/984
