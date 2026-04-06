from pydantic import BaseModel, ConfigDict, Field


class TagPublic(BaseModel):
    id: int
    name: str = Field(..., min_length=3, max_length=30, description="Tag name")

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Tag name")


class TagUpdate(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Tag name")


class TagWithCount(TagPublic):
    uses: int
