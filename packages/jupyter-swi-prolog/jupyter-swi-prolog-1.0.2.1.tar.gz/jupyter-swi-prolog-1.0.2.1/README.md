# SWI-Prolog Kernel for Jupyter

This is a simple wrapper kernel for SWI Prolog.

## Quick Start

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fdbgit.prakinf.tu-ilmenau.de%2Fertr8623%2Fjupyter-swi-prolog.git/master)

## Table of Contents

- [Setup](#setup)
    - [Using pip](#using-pip)
    - [Using Docker](#using-docker)
- [Usage](#usage)

## Setup

### Using pip

Run `pip` to install the corresponding package from [pypi](https://pypi.org/project/jupyter-swi-prolog/) **after**
Jupyter is already installed.

```bash
pip install jupyter-swi-prolog
```

Register the kernel.

```bash
jupyter kernelspec install <path to the site-packages directory>/swi_prolog_kernel
```

Now start Jupyter the usual way and the kernel should be available.

### Using Docker

Execute the following command to pull a and run a prepared image.

```bash
docker run -p 8888:8888 troebs/jupyter:swi-prolog
```

This image can also be used with JupyterHub and the
[DockerSpawner / SwarmSpawner](https://github.com/jupyterhub/dockerspawner)
and probably with the
[kubespawner](https://github.com/jupyterhub/kubespawner).
You can also build your own image using the [Dockerfile](Dockerfile) in the repository.

## Usage

An example can be found [in the repository](example/).

**Please note**: `consult` is usually used to read facts and rules from a Prolog source file. To avoid the need for
separate files, the magic command `%%CONSULT` is supported, which replaces this file with the contents of a cell in the
Jupyter notebook.
