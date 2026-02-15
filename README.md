# CLUBB-ML: A Fork of The CLUBB Singe Column Atmospheric Model Implementing a Machine Learning Convection Parameterisation

This fork of the CLUBB model implements a [new subgrid parameterisation, CLUBBiNN](https://github.com/adconnolly/CLUBBiNN).
The parameterisation is a machine learning implementation using a neural net trained
on high-resolution LES simulations to provide a better estimate for the coefficient C14
relating to the dissipation of turbulent kinetic energy.

The work is contained in a `CLUBB_ML` branch which is based off of the `dcd21c9` commit from
the [`larson-group/clubb_release` branch](https://github.com/larson-group/clubb_release).

The main CLUBB README is not changed and can be found in [`README`](./README).
Information specific to running this fork of CLUBB is included in this README.md file.


## Using this model

### Obtaining CLUBB

Clone a copy of this repository from git and ensure you are on the `CLUBB_ML` branch.
```
git clone git@github.com:m2lines/clubb_ML.git
cd clubb_ML/
git checkout CLUBB_ML
```

### Obtaining and building `FTorch`

To use PyTorch-based neural nets in CLUBB, we use
[`FTorch`](https://github.com/Cambridge-ICCS/FTorch) which needs to
be built on the system before we build CLUBB.

To install `FTorch` follow the general instructions in the
[`FTorch` documentation](https://github.com/Cambridge-ICCS/FTorch).

> [!NOTE]
> The location of the `FTorch` install will be required later when building CAM.

> [!NOTE]
> The environment and compilers used to build FTorch should match those
> used to build CLUBB. Currently CLUBB is only supported to be built with
> `ifx` when using FTorch.

### Building CLUBB

CLUBB can be built, linking to FTorch, using the `ifx` compiler.
This is facilitated by modifications that have been made to the
`compile/config/linux_x86_64_ifort.bash` file. Similar modifications
could be made for other compilers.

Before building CLUBB one needs to add the location of the FTorch install to the
`PKG_CONFIG_PATH` environment variable to allow the build process to locate and link
at build time.
This can be done with the following:
```bash
export PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:</path/to/FTorch-install>/lib64/pkgconfig
```
where `</path/to/FTorch-install>` is the path set during installation of FTorch.

Once this is done CLUBB can be built in the normal way using:
```bash
cd compile
./compile.bash -c config/linux_x86_64_ifort.bash
```

### Creating and running a case

To run one of the default cases, e.g. BOMEX, with the modified CLUBB navigate to the
run scripts directory and execute the run script with the relevant arguments as usual:
```bash
cd ../run_scripts/
./run_scm.bash bomex
```

Output will be placed in the `output/` directory


## CLUBB Documentation

The original CLUBB README can be found in [`README`](./README).
The current document deetails the changes made for coupling to FTorch
and implementing ML schemes within CLUBB.

Documentation for CLUBB can be found at the following DOI:
[10.48550/arXiv.1711.03675](https://doi.org/10.48550/arXiv.1711.03675)


## Authors and Acknowledgments

The original CLUBB code is written and maintained by the [Larson Group](https://sites.uwm.edu/vlarson/clubb/).

The modifications in this fork to couple FTorch and use neural net parameterisations
was performed by research software engineer [Jack Atkinson](https://jackatkinson.net/)
of the [Institute of Computing for Climate Science (ICCS)](https://iccs.cam.ac.uk/).

Subgrid schemes to be coupled were trained by [Alex Connolly](https://adconnolly.github.io/)
of the [Gentine Lab](https://gentinelab.eee.columbia.edu/home) as part of the CLUBBiNN
project.


## Contributing

Contributions to the repository are welcome from members of [M2Lines](https://m2lines.github.io/) and [ICCS](https://iccs.cam.ac.uk/).

Open tickets can be viewed at [**Issues**](https://github.com/m2lines/CLUBB_ML/issues).

To contribute, find a relevant issue or open a new one and assign yourself to work on it.
Then create a branch in which to add your contribution and open a pull request.
Once ready assign a reviewer and request a code review.
Merging should only be performed once a reviewer has approved the changes.

Interested contributors from outside M2Lines are invited to comment on issues to
propose solutions.
