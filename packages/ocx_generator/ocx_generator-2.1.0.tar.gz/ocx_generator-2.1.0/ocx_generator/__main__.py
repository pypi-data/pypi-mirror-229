#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module script entry point."""
# System imports
import warnings, sys
# Third party imports
from loguru import logger
# Module imports
from  ocx_generator.cli import databinding
from ocx_generator.utils.logging import LoguruHandler, showwarning




def main():
    databinding()

if __name__ == "__main__":
    main()