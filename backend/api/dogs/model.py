from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Dog(Base):
    __tablename__ = "dogs"
    breed = Column(String, primary_key=True, index=True)
    image = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<Dog(breed={self.breed}, image={self.image})>"

    def to_dict(self) -> dict:
        return {
            "breed": self.breed,
            "image": self.image,
        }

    def from_dict(self, data: dict) -> None:
        self.breed = data.get("breed", self.breed)
        self.image = data.get("image", self.image)

    @classmethod
    def create_from_dict(cls, data: dict) -> "Dog":
        dog = cls()
        dog.from_dict(data)
        return dog

    def update_from_dict(self, data: dict) -> None:
        self.from_dict(data)
