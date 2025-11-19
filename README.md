# tcode-api

`tcode-api` is a python package that provides an API for scripting trilobot platform actions.

## Installation

Trilobio's fleet controllers come pre-installed with the `tcode-api` package in a development environment.
However, if you wish to manually install the package in order to trial the API, or to develop scripts locally,

### Python Requirements
`tcode-api` runs on modern python, and requires python version 3.11 or higher. For the most
up-to-date python versioning information, see the `pyproject.toml` file at the repository's root.

### Package Installation

you can do so via one of the following methods:

#### Using `uv` (recommended)

Internally, Trilobio developers use `uv` to manage python environments and tooling.

To install `uv`, follow the instructions on [docs.astral.sh/uv/](https://docs.astral.sh/uv/getting-started/installation/)


#### using pip (not recommented)

Using pip to install `tcode-api` is not recommended as typical pip usage leads to poorly managed
environments and dependency conflicts. However, if you wish to proceed with pip, you can do so.

Example: To install `tcode-api` version `v1.25.1`, run the following command:

```python -m pip install tcode-api @ git+https://https://github.com/trilobio/tcode-api.git@v1.25.1```

Further documentation on using pip with version control systems (VCS) can be found at:
https://pip.pypa.io/en/stable/topics/vcs-support/

