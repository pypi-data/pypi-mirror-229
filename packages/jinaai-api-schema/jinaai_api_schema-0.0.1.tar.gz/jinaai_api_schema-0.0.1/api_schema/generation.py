from typing import Dict, Optional, Union

from docarray import BaseDoc, DocList
from docarray.documents import ImageDoc
from pydantic import Field

from .base import BaseBodyModel


class ImagePromptBodyModel(BaseBodyModel, BaseDoc):
    prompt: str
    negative_prompt: Optional[str] = None

    seed: Optional[int] = None
    sampler: Optional[str] = None
    num_inference_steps: Optional[int] = 50
    num_images_per_prompt: Optional[int] = 1

    height: Optional[int] = None
    width: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "model": "runwayml/stable-diffusion-v1-5",
                "prompt": "A photo of a cat",
                "negative_prompt": "A photo of a dog",
                "seed": 42,
            },
        }


class ImageGenerationResponseModel(BaseDoc):
    images: DocList[ImageDoc] = DocList[ImageDoc]()
    usage: Dict[str, Union[int, float]] = Field(
        description='The usage of the model', default={}
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "images": ["https://picsum.photos/200"],
            },
        }
