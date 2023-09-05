#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
"""Module script entry point."""
# System imports
import warnings, sys
# Third party imports
from loguru import logger
# Module imports
from  ocx_generator.cli import databinding
from ocx_generator.utils.logging import LoguruHandler, showwarning


# Logging config for application
config = {
    "handlers": [
        {"sink": sys.stdout, "format": "{time} - {message}"},
        {"sink": str.join(__name__, ".log"), "serialize": True},
    ],
}

# Connect xsdata logger to loguru
handler = LoguruHandler()
logger.add(handler)


# Log warnings as well
showwarning_ = warnings.showwarning


def main():
    databinding()

if __name__ == "__main__":
    logger.enable('ocx_generator')
    handler.emit_warnings()
    main()