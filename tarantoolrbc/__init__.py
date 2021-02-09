# -*- coding: utf-8 -*-
# pylint: disable=C0301,W0105,W0401,W0614

import logging
from .client import SelectedConnection

__all__ = ["SelectedConnection"]
__version__ = "0.0.2"

logging.getLogger(__name__).addHandler(logging.NullHandler())
