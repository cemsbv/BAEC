# BAEC Model Generator SDK

Python SDK to create Model Generators and add them into the BAEC platform.

[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Coverage Status](https://coveralls.io/repos/github/cemsbv/py-pilecore/badge.svg)](https://coveralls.io/github/cemsbv/py-pilecore)

This repository is created by [CEMS BV](https://cemsbv.nl/).

# Installation

To install a package in this repository run:

`$ pip install baec`

## ENV VARS

To use `baec` with `FitCore` to fit and predict settlements, add the follow ENV vars to your environment. Or provide them when asked.

```
* NUCLEI_TOKEN
    - Your NUCLEI user token
```

You can obtain your `NUCLEI_TOKEN` on [NUCLEI](https://nuclei.cemsbv.io/#/).
Go to `personal-access-tokens` and create a new user token.

# Contribution

## Environment

We recommend developing in Python 3.12 with a clean virtual environment (using `virtualenv` or `conda`), installing the requirements from the requirements.txt file:

Example using `virtualenv` and `pip` to install the dependencies in a new environment .env on Linux:

```bash
python -m venv .env
source .env/bin/activate
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install -e .
```

## Documentation

Build the docs:

```bash
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install .

sphinx-build -b html docs public
```

## Format

We format our code with black and isort.

```bash
black --config "pyproject.toml" src/baec tests example
isort --settings-path "pyproject.toml" src/baec tests example
```

## Lint

To maintain code quality we use the GitHub super-linter.

To run the linters locally, run the `run_super_linters.sh` bash script from the root directory.

## UnitTest

Test the software with the use of coverage:

```bash
set -a; source ./*.env; set +a
python -m pip install --upgrade pip setuptools
pip install -r requirements.txt
pip install -e .
coverage run -m pytest
```

## Requirements

Requirements are autogenerated by the `pip-compile` command with python 3.10

Install pip-tools with:

```bash
pip install pip-tools
```

Generate requirements.txt file with:

```bash
pip-compile --extra=test --extra=lint --extra=docs --extra=aws --output-file=requirements.txt pyproject.toml
```

Update the requirements within the defined ranges with:

```bash
pip-compile --upgrade --extra=test --extra=lint --extra=docs --extra=aws --output-file=requirements.txt pyproject.toml
```
