# ocx-databinding
CLI python script for managing OCX schema databinding and versioning according to PEP 440.
See the documentation of [xsdata](https://xsdata.readthedocs.io/en/latest/) for details on the python databindings.

## Installation

    pip install ocx_generator

## Usage
    > python -m ocx_versioning --help
    Usage: ocx_generator "module_name" "version_string"
    
    --help: Prints this message and exits.
    --version: Prints the version number and exits.
    >
    > python -m ocx 1.0.0
    Updating the configuration file xsdata.xml in module ocx
    New package name is ocx_100 with version: 1.0.0



    

