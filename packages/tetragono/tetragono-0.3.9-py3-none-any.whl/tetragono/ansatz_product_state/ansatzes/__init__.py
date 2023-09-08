#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2022-2023 Hao Zhang<zh970205@mail.ustc.edu.cn>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from .marshall import Marshall
from .product_ansatz import ProductAnsatz
from .sum_ansatz import SumAnsatz
try:
    import torch
except ModuleNotFoundError:

    class MissingTorchMeta(type):

        def __new__(cls, name, bases, attrs):
            attrs["__init__"] = cls._generate_init_(name)
            return type.__new__(cls, name, bases, attrs)

        @staticmethod
        def _generate_init_(name):

            def __init__(self, *args, **kwargs):
                raise RuntimeError("torch needed for " + name)

            return __init__

    class ConvolutionalNeural(metaclass=MissingTorchMeta):
        pass

    class OpenString(metaclass=MissingTorchMeta):
        pass

    class ClosedString(metaclass=MissingTorchMeta):
        pass
else:
    from .convolutional_neural import ConvolutionalNeural
    from .open_string import OpenString
    from .closed_string import ClosedString
