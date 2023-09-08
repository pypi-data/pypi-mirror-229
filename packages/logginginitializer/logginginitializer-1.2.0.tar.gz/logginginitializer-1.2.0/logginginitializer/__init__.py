# -*- coding: utf-8 -*-
"""Mini library to provide an easy way to initialize the Python logging module."""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "RWS Datalab"
__email__ = "datalab.codebase@rws.nl"
__version__ = "1.2.0"
