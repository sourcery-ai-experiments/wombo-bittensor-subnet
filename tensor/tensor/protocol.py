# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2024 WOMBO
from enum import Enum
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from typing import List, Optional
from io import BytesIO
import base64

import bittensor as bt
from PIL import Image

from image_generation_protocol.io_protocol import ImageGenerationInputs, ImageGenerationOutput


def load_base64_image(data: bytes) -> Image.Image:
    return Image.open(BytesIO(base64.b64decode(data)))


class NeuronType(Enum):
    MINER = "miner"
    VALIDATOR = "validator"
    UNKNOWN = "unknown"


class NeuronInfoSynapse(bt.Synapse):
    neuron_type: NeuronType = NeuronType.UNKNOWN


class ImageGenerationSynapse(bt.Synapse):
    inputs: ImageGenerationInputs
    output: Optional[ImageGenerationOutput]


class ImageGenerationClientSynapse(bt.Synapse):
    inputs: ImageGenerationInputs
    images: Optional[List[bytes]]

    def deserialize(self) -> List[Image.Image]:
        f"""
        Assumes the {self.images} field is filled by axon
        """
        return [load_base64_image(data) for data in self.images]
