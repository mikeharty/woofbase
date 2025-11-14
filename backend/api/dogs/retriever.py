from clients.olive import OliveClient
from .model import Dog
from common.db import get_db
from common.log import Log
from api.dogs.service import DogService


class DogRetriever:

    @staticmethod
    async def sync_dogs() -> None:
        Log.info("Starting dog synchronization with Olive API")
        try:
            dog_service = DogService()
            client = OliveClient()
            olive_dogs = await client.fetch_all(endpoint="dogs")
            olive_dog_breeds = {dog["breed"] for dog in olive_dogs}
            Log.info(f"Fetched {len(olive_dogs)} dogs from Olive API")
            Log.debug(f"Olive dog breeds: {olive_dog_breeds}")
            local_dogs = dog_service.get_all()
            local_dog_breeds = {dog.breed for dog in local_dogs}
            Log.info(f"Fetched {len(local_dogs)} local dogs from database")
            Log.debug(f"Local dog breeds: {local_dog_breeds}")
            for olive_dog in olive_dogs:
                if olive_dog["breed"] not in local_dog_breeds:
                    dog_service.add(olive_dog)
                    Log.info(f"Added new dog to local database: {olive_dog['breed']}")

                elif olive_dog["breed"] in local_dog_breeds:
                    local_dog = dog_service.find(olive_dog["breed"])
                    if local_dog is not None:
                        if olive_dog.get("image") and local_dog.image != olive_dog.get(
                            "image"
                        ):
                            dog_service.update(local_dog, olive_dog)
                            Log.info(
                                f"Updated dog '{local_dog.breed}' in database with new image: {olive_dog.get('image')}"
                            )

            for local_dog in local_dogs:
                if (
                    local_dog.breed not in olive_dog_breeds
                    and not local_dog.breed.startswith("#")  # type: ignore
                ):
                    dog_service.remove(local_dog)
                    Log.info(f"Removed dog from local database: {local_dog.breed}")

            Log.info("Dog synchronization completed successfully")
        except Exception as error:
            Log.error(f"Error during dog synchronization!", error=error)
