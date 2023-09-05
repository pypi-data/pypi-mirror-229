<div align="center">
<img src="docs/assets/images/holab_logo.png" alt="logo"></img>
<p><i>Hologram Optimization Laboratory</i></p>
</div>

Holab is a tool for designing acoustic lenses that generate arbitrarily complex holograms. It is written on top of `jax` and `jwave` to allow for fast GPU computations, as well as to guarantee great flexibility in designing the holograms and the lenses requiremends, using automatic differentiation.

## Install

To install the `holab`, make sure that you have [installed jax with GPU support](https://github.com/google/jax#installation). Then, simply use

```bash
pip install holab
```

## Getting started

Please visit the [documentation](https://github.com/ucl-bug/holab/) for a detailed description of the software and its usage. An example is provided [as a jupyter notebook](docs/example.ipynb).

<br/>

## Citation

```bibtex
@misc{stanziola2023physicsbased,
      title={Physics-Based Acoustic Holograms},
      author={Antonio Stanziola and Ben T. Cox and Bradley E. Treeby and Michael D. Brown},
      year={2023},
      eprint={2305.03625},
      archivePrefix={arXiv},
      primaryClass={cs.SD}
}
```

<br/>

## Related projects
- [jolab](https://github.com/DylanMMarques/Jolab.jl): Jolab is a free and open-source Julia package to simulate light propagation in optical systems. From Dylan Marques et al.
- [jwave](https://github.com/ucl-bug/jwave): A JAX-based research framework for differentiable and parallelizable acoustic simulations, on CPU, GPUs and TPUs.
