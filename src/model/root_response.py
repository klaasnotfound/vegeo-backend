from pydantic import BaseModel, Field
from pydantic.alias_generators import to_camel


class RootResponseSchema(BaseModel):
    name: str = Field(title="Name of the API server")
    version: str = Field(title="Version of the API server")

    model_config = {
        "alias_generator": to_camel,
        "populate_by_name": True,
        "from_attributes": True,
        "json_schema_extra": {"examples": [{"name": "Vegeo API", "version": "0.1.0"}]},
    }
