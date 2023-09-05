#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Generate code from xml schemas, webservice definitions and any xml or json document."""
# System imports
from pathlib import Path
import subprocess
from subprocess import PIPE
import warnings
from typing import Iterator
# Third party packages
from loguru import logger
import packaging.version
import xsdata.exceptions
from packaging.version import Version, parse
from xsdata.models.config import GeneratorConfig


# Project imports

def generate(source, package_name:str, version: str, config_file: str, stdout:bool = False, recursive:bool=True)->bool:
    """ Generate code from xml schemas, webservice definitions and any xml or json document, see  https://xsdata.readthedocs.io/en/latest/
        The input source can be either a filepath, uri or a directory containing  xml, json, xsd and wsdl files.
        If the config file xsdata.xml does not exist, it will be created with the following values set:

       Arguments:
            package_name: The name of the pypi package. A folder with the name of the package wil be created and the databinding will be generated here.
            version: The version from the source schema
            config_file: name of config file. Default: xsdata.xml. Will be created in the  package folder
            recursive:  Search files recursively in the source directory

    Example:

           >>> import ocx_generator.generator as generator
           >>> generator.generate('unitsMLSchema.lite.xsd', version='0.9.18', config_file='xsdata.xml', stdout=False, recursive=False)
            Updating the configuration file xsdata.xml in module ocx
            New package name is ocx_100 with version: 1.0.0

    """
    package_folder = Path.cwd() / Path(package_name)
    package_folder.mkdir(parents=True, exist_ok=True)
    try:
        v= parse(version)
        if v.is_prerelease:
            pr1, pr2 = v.pre
            databinding = f'{package_name}_{v.major}{v.minor}{v.micro}{pr1}{pr2}'
        else:
            databinding = f'{package_name}_{v.major}{v.minor}{v.micro}'
        destination_folder = package_folder / Path(databinding)
        destination_folder.mkdir(parents=True, exist_ok=True)
        #os.chdir(str(destination_folder.resolve()))
        # if config_file.exists():
        #     config = GeneratorConfig.read(config_file.resolve())
        #     logger.info(f'Updating the configuration file {config_file} in module {destination_folder}')
        # else:
        #     logger.info(f'Initializing configuration file {config_file.resolve()}')
        config = GeneratorConfig.create()
        # OCX databindings defaults
        config.output.docstring_style = 'Google'
        # The package name
        config.output.package = databinding
        # Create a single package
        config.output.structure_style = 'single-package'
        # Unnest classes
        config.output.unnest_classes = False
        logger.info(f'New databinding package name is {databinding} with version: {version} is created in {package_folder.resolve()}')
        config_file = destination_folder / Path(config_file)
        with config_file.open("w") as fp:
            config.write(fp, config)
        try:
            return_code = subprocess.call(f'xsdata generate {source} -c {config_file.resolve()} ',
                                    shell=True, cwd=destination_folder.resolve(),
                                          #stdout=PIPE
                                          )
            if return_code != 0:
                logger.error(f'xsdata generate failed with return code {return_code}')
            return True
        except xsdata.exceptions.CodeGenerationError as e:
            logger.error(f'xsdata generate failed:  {e}')
            return False
    except packaging.version.InvalidVersion as e:
        print(e)
        return False