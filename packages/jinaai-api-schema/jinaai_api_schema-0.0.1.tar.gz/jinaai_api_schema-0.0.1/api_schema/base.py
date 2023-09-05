from pydantic import BaseModel, Field


class BaseBodyModel(BaseModel):
    model: str = Field(description='The identifier of the model.')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
