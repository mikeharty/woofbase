from pydantic import BaseModel
from typing import Optional


class DogSchema(BaseModel):
    breed: str
    image: Optional[str] = None
    video: Optional[str] = None

    class Config:
        from_attributes = True


class DogPageResult(BaseModel):
    dogs: list[DogSchema]
    page: int
    cached: bool
    total_dogs: int
    total_pages: int


class DogCreateSchema(BaseModel):
    breed: str
    image: Optional[str] = None


class DogUpdateSchema(BaseModel):
    breed: Optional[str] = None
    image: Optional[str] = None
