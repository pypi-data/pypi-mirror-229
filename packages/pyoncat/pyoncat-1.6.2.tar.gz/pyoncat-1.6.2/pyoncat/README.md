Welcome to PyONCat, a Python client designed to facilitate interaction with the ONCat API.

## Introduction

[ONCat](https://oncat.ornl.gov) is a data cataloging system that assists scientists and researchers in managing and navigating their data. It aggregates metadata about data, experiments and users from various systems, offering a convenient and manageable way to access neutron data and associated information.

The `pyoncat` package serves as a Python client to more easily interact with the ONCat API.

## Installation

### Requirements

- Python version: `>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4`
- Python packages: `requests`
- Optional packages for authenticated API access: `oauthlib`, `requests-oauthlib`

### Installing with pip

For basic unauthenticated installation, use the following command:

```sh
pip install pyoncat
```

To install the package with support for the authenticated version of the API, use the following command:

```sh
pip install pyoncat oauthlib requests-oauthlib
```

### Installing with Conda

A Conda package will be available soon as an alternative installation method.

## Usage

### Authenticating with the API

To use the authenticated version of the API, you need to obtain credentials from an ONCat administrator. Please contact ONCat Support at [oncat-support@ornl.gov](mailto:oncat-support@ornl.gov) to request credentials.

### Examples

For usage examples, please refer to the API documentation at [oncat.ornl.gov](https://oncat.ornl.gov) as well as the iPython Notebook tutorial available at this [link](https://github.com/neutrons/IPythonNotebookTutorial/blob/master/notebooks/PyONCat.ipynb).

## Getting Help

If you encounter any issues or require assistance with the `pyoncat` package, please reach out to the ONCat Support at [oncat-support@ornl.gov](mailto:oncat-support@ornl.gov).

## Resources

- [Official Documentation](https://oncat.ornl.gov)
- [iPython Notebook Tutorial](https://github.com/neutrons/IPythonNotebookTutorial/blob/master/notebooks/PyONCat.ipynb)

Thank you for using PyONCat!
