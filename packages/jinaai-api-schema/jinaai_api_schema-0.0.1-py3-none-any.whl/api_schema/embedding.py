from typing import Dict, List, Union

from docarray import BaseDoc, DocList
from docarray.documents import ImageDoc
from docarray.typing import NdArray
from pydantic import Field

from .base import BaseBodyModel


class TextEmbeddingBodyModel(BaseBodyModel, BaseDoc):
    model: str = Field(
        description='The identifier of the model.\n'
        '\nAvailable models and corresponding param size and dimension:\n'
        '- `jina-embedding-t-en-v1`,\t14m,\t312\n'
        '- `jina-embedding-s-en-v1`,\t35m,\t512 (default)\n'
        '- `jina-embedding-b-en-v1`,\t110m,\t768\n'
        '- `jina-embedding-l-en-v1`,\t330,\t1024\n'
        '\nFor more information, please checkout our [technical blog](https://arxiv.org/abs/2307.11224).\n',
        default='jina-embedding-s-en-v1',
    )
    texts: List[str] = Field(
        description='List of texts to embed. The length of the list must be between `1` and `100`',
        min_items=1,
        max_items=100,
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "model": "jina-embedding-s-en-v1",
                "texts": ["Hello, world!"],
            },
        }


class ImageEmbeddingBodyModel(BaseBodyModel, BaseDoc):
    images: DocList[ImageDoc]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "model": "openai-clip-vit-b-32",
                "images": ["https://picsum.photos/200"],
            },
        }


class EmbeddingResponseModel(BaseDoc):
    embeddings: NdArray = Field(description='The embedding of the text', default=[])

    usage: Dict[str, Union[int, float]] = Field(
        description='The usage of the model', default={}
    )

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {NdArray: lambda v: v.tolist()}
        schema_extra = {
            "example": {
                "embeddings": [[0.1, 0.2, 0.3]],
                "usage": {"prompt_tokens": 3, "total_tokens": 3},
            }
        }
