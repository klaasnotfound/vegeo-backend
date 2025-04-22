from pydantic import BaseModel, Field


class RootResponseSchema(BaseModel):
    name: str = Field(title="Name of the API server")
    version: str = Field(title="Version of the API server")

    model_config = {"json_schema_extra": {"examples": [{"name": "Vegeo API", "version": "0.1.0"}]}}
