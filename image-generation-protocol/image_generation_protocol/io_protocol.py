import random
from typing import Annotated, TypeAlias

from pydantic import BaseModel, Field

DEFAULT_WIDTH = 768
DEFAULT_HEIGHT = 1344
DEFAULT_STEPS = 20
DEFAULT_GUIDANCE = 7.0

MIN_SIZE = 512
MAX_SIZE = 1536
MAX_STEPS = 100


GenerationResolution = Annotated[int, Field(ge=MIN_SIZE, le=MAX_SIZE)]
Frames: TypeAlias = bytes | None


class ImageGenerationInputs(BaseModel):
    """Inputs that should be communicated E2E directly from the client to the image generator"""

    prompt: str = ""  # Has a default as it needs to be default constructable
    prompt_2: str | None = None
    height: GenerationResolution = DEFAULT_HEIGHT
    width: GenerationResolution = DEFAULT_WIDTH
    num_inference_steps: Annotated[int, Field(gt=0, le=MAX_STEPS)] = DEFAULT_STEPS
    guidance_scale: float = DEFAULT_GUIDANCE
    negative_prompt: str | None = None
    negative_prompt_2: str | None = None
    num_images_per_prompt: Annotated[int, Field(gt=0, le=4)] = 1
    seed: Annotated[int | None, Field(default_factory=lambda: random.randint(0, (2**32) - 1))]
    controlnet_conditioning_scale: float = 0.0


class ImageGenerationOutput(BaseModel):
    frames: Frames
    images: list[bytes]


class ValidationInputs(BaseModel):
    input_parameters: ImageGenerationInputs
    frames: Frames
