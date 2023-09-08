# -*- coding: utf-8 -*-
# @Author: Muhammad Umair
# @Date:   2023-01-06 14:55:34
# @Last Modified by:   Hannah Shader
# @Last Modified time: 2023-09-07 21:24:38


__version__ = "0.0.2a3"

from .api import GailBot
from .core.engines import Engine, Watson, WatsonAMInterface, WatsonLMInterface
from .plugins import Plugin, Methods
from .services import GBPluginMethods, UttDict, UttObj
