from fastapi import APIRouter

from api.dogs.service import DogService
from api.dogs.schema import DogPageResult
from clients.olive import OliveClient

router = APIRouter()
client = OliveClient()
dog_service = DogService()


@router.get("/dogs")
def list(page: int = 1) -> DogPageResult:
    return dog_service.get_page(page=page)
