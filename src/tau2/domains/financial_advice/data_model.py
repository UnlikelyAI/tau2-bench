from pydantic import BaseModel, Field

class Product(BaseModel):
    """A financial product."""

    id: str = Field(description="The ID of the product")
    name: str = Field(description="The name of the product")
    detail: str = Field(description="The detail of what the product provides")
