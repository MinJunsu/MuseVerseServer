from fastapi import APIRouter, status

from starlette.requests import Request

from app.database.schema import Profiles, Inventories, Items
from app.models import Profile


router = APIRouter()


@router.get('/accounts/me', status_code=status.HTTP_200_OK, response_model=Profile)
async def get_me(request: Request):
    profile = Profiles.get(user=request.user.id)
    items = Items.filter(id__in=[element.item for element in Inventories.filter(
        owner=Profiles.get(user=request.user.id).id).all()]).all()
    profile.inventories = items
    return profile
