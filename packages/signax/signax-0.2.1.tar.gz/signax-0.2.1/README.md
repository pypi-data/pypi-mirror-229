# Signax: Computing signatures in JAX

[![Actions Status][actions-badge]][actions-link]
[![Codecov Status][codecov-badge]][codecov-link]
[![Documentation Status][rtd-badge]][rtd-link]
[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/Anh-Tong/signax/workflows/CI/badge.svg
[actions-link]:             https://github.com/Anh-Tong/signax/actions
[codecov-badge]:            https://codecov.io/gh/anh-tong/signax/branch/main/graph/badge.svg?token=SU9HZ9NH70
[codecov-link]:             https://codecov.io/gh/anh-tong/signax
[pypi-link]:                https://pypi.org/project/signax/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/signax
[pypi-version]:             https://img.shields.io/pypi/v/signax
[rtd-badge]:                https://readthedocs.org/projects/signax/badge/?version=latest
[rtd-link]:                 https://signax.readthedocs.io/en/latest/?badge=latest
<!-- prettier-ignore-end -->

## Goal

To have a library that supports signature computation in JAX. See
[this paper](https://arxiv.org/abs/1905.08494) to see how to adopt signatures in
machine learning.

This implementation is inspired by
[patrick-kidger/signatory](https://github.com/patrick-kidger/signatory).

## Examples

Basic usage

```python
import jax
import jax.random as jrandom
import signax


key = jrandom.PRNGKey(0)
depth = 3

# compute signature for a single path
length = 100
dim = 20
path = jrandom.normal(shape=(length, dim), key=key)
output = signax.signature(path, depth)
# output is a list of array representing tensor algebra

# compute signature for batches (multiple) of paths
path = jrandom.normal(shape=(batch_size, length, dim), key=key)
# new signax API can handle this case two
output = signax.signature(path, depth)
```

Integrate with the [equinox](https://github.com/patrick-kidger/equinox) library

```python
import equinox as eqx
import jax.random as jrandom

from signax.module import SignatureTransform

# random generator key
key = jrandom.PRNGKey(0)
mlp_key, data_key = jrandom.split(key)

depth = 3
length, dim = 100, 3

# create a signature transform at the specified depth
signature_layer = SignatureTransform(depth=depth)

# stack a MLP layer after that
last_layer = eqx.nn.MLP(
    depth=1, in_size=3 + 3**2 + 3**3, width_size=4, out_size=1, key=mlp_key
)

model = eqx.nn.Sequential(layers=[signature_layer, last_layer])
x = jrandom.normal(shape=(length, dim), key=data_key)
output = model(x)
```

Also, check the notebooks in `examples` folder for some experiments that
reproduce the results of the
[deep signature transforms paper](https://arxiv.org/abs/1905.08494).

## Installation

Via pip

```
python3 -m pip install signax
```

Via source

```
git clone https://github.com/anh-tong/signax.git
cd signax
python3 -m pip install -v -e .
```

## Parallelism

This implementation makes use of `jax.vmap` to perform the parallelism over
batch dimension.

Paralelism over chunks of paths is done using `jax.vmap` as well.

A quick comparison can be found at in the notebook `examples/compare.ipynb`.
Below plots are comparison of forward and backward pass in both GPU and CPU for
path `size=(32, 128, 8)` and signature `depth=5`

<table>
<thead>
  <tr>
    <th >Forward</th>
    <th >Backward</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>
        <img width="300" height="170" src="./assets/forward_gpu.png">
    </td>
    <td>
        <img width="300" height="170" src="./assets/backward_gpu.png">
    </td>
  </tr>
  <tr>
    <td>
        <img width="300" height="170" src="./assets/forward_cpu.png">
    </td>
    <td>
        <img width="300" height="170" src="./assets/backward_cpu.png">
    </td>
  </tr>
</tbody>
</table>

## Why is using pure JAX good enough?

Because JAX make use of just-in-time (JIT) compilations with XLA, Signax can be
reasonably fast.

We observe that the performance of this implementation is similar to Signatory
in CPU and slightly better in GPU. It could be because of the optimized
operators of XLA in JAX. Note that
[Signatory](https://github.com/patrick-kidger/signatory) contains highly
optimized C++ source code (PyTorch with Pybind11).

## Acknowledgement

This repo is based on

- [Signatory](https://github.com/patrick-kidger/signatory)
- [Deep-Signature-Transforms](https://github.com/patrick-kidger/Deep-Signature-Transforms)
- [Equinox](https://github.com/patrick-kidger/equinox)
