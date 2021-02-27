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
   - Default settings enable CUDA support. In order to disable it one could
     `nix-shell --arg with_cuda false`.
4. Compile Protobuf wrappers `protoc src/galang/serbin.proto --python_out=.`
5. Run `./ipython.sh` helper to enter IPython shell.
6. ... (work is in progress)


References
----------

**Program Synthesis**

* [TF-Coder at OpenReview](https://openreview.net/forum?id=nJ5Ij53umw2)

**Nix**

* [Python development in NixOS](https://nixos.wiki/wiki/Python)

**Python**

* [Protocol buffers docs, proto2](https://developers.google.com/protocol-buffers/)
* [Protocol buffers docs, proto3](https://developers.google.com/protocol-buffers/docs/proto3)
* https://www.datadoghq.com/blog/engineering/protobuf-parsing-in-python/
* [Struct](https://docs.python.org/3/library/struct.html)

**Pytorch**

* [torch.utils.data](https://pytorch.org/docs/1.7.1/data.html?highlight=torch%20utils%20data#module-torch.utils.data)
* [PyTroch data loading tutorial](https://pytorch.org/tutorials/beginner/data_loading_tutorial.html)

**Pandas**

* [GroupBy API Reference](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html)
* [GroupBy User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html)

**Altair**

* [Altair gallery](https://altair-viz.github.io/gallery/)
* [Altair common customization](https://altair-viz.github.io/user_guide/customization.html)

**LaTeX**

* [LaTeX-Tutorial](https://www.latex-tutorial.com/)
* [Algorithms](https://shantoroy.com/latex/how-to-write-algorithm-in-latex/)
* [UtilSnips](https://github.com/SirVer/ultisnips)
* [Vim+LaTex guide (in Russian)](https://m.habr.com/ru/post/445066/)
* [Minted](https://www.overleaf.com/learn/latex/Code_Highlighting_with_minted)
* [A4Paper](https://www.overleaf.com/learn/latex/page_size_and_margins)
* Literate programming:
  - [Lepton](https://www.math.univ-paris13.fr/~lithiao/ResearchLepton/Lepton.html)
    + [Lepton Sources](https://github.com/slithiaote/lepton)
  - [Pythontex](https://ctan.math.illinois.edu/macros/latex/contrib/pythontex/pythontex.pdf)
    + [Pythontex Sources](https://github.com/gpoore/pythontex)
* Problems
  - [Footnotes in tables](https://tex.stackexchange.com/questions/35200/footnotes-in-tabulars)
* [Math fonts](https://www.overleaf.com/learn/latex/Mathematical_fonts)
* HTML
  - https://tug.org/tex4ht/

**Math**

* [Mean and Variance](https://online.stat.psu.edu/stat414/lesson/24/24.3)
* [Sample Mean and Variance](https://online.stat.psu.edu/stat414/lesson/26/26.3)
* [MathExchange question asking about Uniformity checks](https://math.stackexchange.com/questions/2435/is-there-a-simple-test-for-uniform-distributions)
* [Kolmogorov-Smirnov test](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test)
  - [SciPy implementation](https://docs.scipy.org/doc/scipy-1.6.0/reference/generated/scipy.stats.kstest.html)

Related issues
--------------

* https://github.com/altair-viz/altair/issues/984
* https://math.stackexchange.com/questions/3973622/explain-the-behavior-of-ks-test-when-testing-for-uniformity
* Nix+SOCKS proxy:
  1. `ALL_PROXY=socks5h://localhost:8001 nix-prefetch-url <URL>`
   - https://blog.emacsos.com/use-socks5-proxy-in-curl.html
  2. `nix-shell`
* [Sharing sessions between pyblock and pyconsole](https://github.com/gpoore/pythontex/issues/55)
* [Labels in PythonTex](https://github.com/gpoore/pythontex/issues/179)

