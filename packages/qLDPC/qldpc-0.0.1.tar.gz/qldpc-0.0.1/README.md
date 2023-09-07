# qLDPC (PREVIEW)

This repository contains tools for constructing and analyzing [quantum low density partity check (qLDPC) codes](https://errorcorrectionzoo.org/c/qldpc).

## Installation

This package requires Python>=3.10, and can be installed from PyPI with
```
pip install -U qldpc
```
To install from source:
```
git clone ...
cd qLDPC
pip install -e .
```

## Features

Notable features include:
- `abstract.py`: module for basic abstract algebra (groups, algebras, and representations thereof).
- `BitCode`: class for representing {classical, linear, binary} error-correcting codes.
- `CSSCode`: general class for constructing [quantum CSS codes](https://errorcorrectionzoo.org/c/css) out of two classical `BitCode`s.
  - Includes options for applying local Pauli transformations (i.e., Pauli deformations of the code), which is useful for tailoring a `CSSCode` to biased noise (see [arXiv:2202.01702](https://arxiv.org/abs/2202.01702)).
  - `CSSCode.get_logical_ops`: method (from [arXiv:0903.5256](https://arxiv.org/abs/0903.5256)) to construct a basis of nontrivial logical operators for a `CSSCode`.
  - `CSSCode.get_distance`: method to compute the code distance (i.e., the smallest weight of a nontrivial logical operator).  Includes options for computing a lower bound (determined by the distances of the underlying `BitCode`s), an upper bound (see [arXiv:2308.07915](https://arxiv.org/abs/2308.07915)), and the exact code distance (with an integer linear program).
- `HGPCode`: class for constructing [hypergraph product codes](https://errorcorrectionzoo.org/c/hypergraph_product) out of two classical `BitCode`s.  Follows the conventions of [arXiv:2202.01702](https://arxiv.org/abs/2202.01702).
- `LPCode`: class for constructing [lifted product codes](https://errorcorrectionzoo.org/c/lifted_product) out of two protographs (i.e., matrices whose entries are elements of a group algebra).  See [arXiv:2012.04068](https://arxiv.org/abs/2012.04068) and [arXiv:2202.01702](https://arxiv.org/abs/2202.01702).
- `QuasiCyclicCode`: class for constructing the quasi-cyclic codes in [arXiv:2308.07915](https://arxiv.org/abs/2308.07915).
- `QTCode`: class for constructing [quantum Tanner codes](https://errorcorrectionzoo.org/c/quantum_tanner) out of (a) two symmetric subsets `A` and `B` of a group `G`, and (b) two classical `BitCode`s with block lengths `|A|` and `|B|`.  See [arXiv:2202.13641](https://arxiv.org/abs/2202.13641) and [arXiv:2206.07571](https://arxiv.org/abs/2206.07571).

## Questions and issues

If this project gains interest and traction, we'll add a documentation webpage to help users get started quickly.  In the meantime, you can explore the extensive documentation and explanations available in the source code.  `qldpc/codes_test.py` in particular contains examples of using the classes and methods described above.

If you have any questions or requests, please open an issue!

## Attribution

If you use this software in your work, please cite with:
```
@misc{perlin2023qldpc,
  author = {Perlin, Michael A.},
  title = {q{LDPC}},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/...}},
}
```
This may require adding `\usepackage{url}` to your LaTeX source file.  Alternatively, you can cite
```
Michael A. Perlin. qLDPC. https://github.com/..., 2023.
```
