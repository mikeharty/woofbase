from common.env import get_env
from common.db import get_db
from common.cache import Cache
from .schema import DogPageResult, DogSchema
from .model import Dog

DOG_CACHE_TTL = get_env("DOG_CACHE_TTL", 60)
DOG_PAGE_SIZE = get_env("DOG_PAGE_SIZE", 15)


class DogService:
    def __init__(self):
        self.session = next(get_db())

    def find(self, breed: str) -> Dog | None:
        dog = self._get_dog_cache(breed) or self._get_dog_db(breed)
        return dog

    def get_page(self, page: int = 1) -> DogPageResult:
        total_dogs = self.session.query(Dog).count()
        cached_page = self._get_dog_page_cache(page)
        if cached_page:
            dogs = cached_page
        else:
            dogs = self._get_dog_page_db(page)

        if page == 1 and not cached_page and len(dogs) > 0:
            dogs.insert(
                0,
                Dog(
                    breed="#1 Doggo",
                    video="https://woof.mikeharty.com/lowkey.mp4",
                    image="https://woof.mikeharty.com/poster.png",
                ),
            )

        return DogPageResult(
            dogs=[DogSchema.model_validate(dog) for dog in dogs],
            page=page,
            cached=bool(cached_page),
            total_dogs=total_dogs,
            total_pages=(total_dogs + DOG_PAGE_SIZE - 1) // DOG_PAGE_SIZE,
        )

    def get_all(self) -> list[Dog]:
        return self.session.query(Dog).all()

    def add(self, dog_data: dict) -> Dog:
        new_dog = Dog.create_from_dict(dog_data)
        self.session.add(new_dog)
        self.session.commit()
        return new_dog

    def update(self, dog: Dog, dog_data: dict) -> Dog:
        for key, value in dog_data.items():
            setattr(dog, key, value)
        self.session.commit()
        return dog

    def remove(self, dog: Dog) -> None:
        self.session.delete(dog)
        self.session.commit()

    def _get_dog_cache(self, breed: str) -> "Dog | None":
        return Cache.get(f"dog_{breed}")

    def _get_dog_page_cache(self, page: int) -> list["Dog"]:
        return Cache.get(f"dogs_page_{page}")

    def _set_dog_page_cache(self, page: int, dogs: list["Dog"]) -> None:
        Cache.set(f"dogs_page_{page}", dogs, ttl=60)

    def _get_dog_db(self, breed: str) -> "Dog | None":
        return self.session.query(Dog).filter(Dog.breed == breed).first()

    def _get_dog_page_db(self, page: int = 1, limit: int = 15) -> list["Dog"]:
        offset = (page - 1) * limit
        dogs = self.session.query(Dog).offset(offset).limit(limit).all()
        self._set_dog_page_cache(page, dogs)
        return dogs
