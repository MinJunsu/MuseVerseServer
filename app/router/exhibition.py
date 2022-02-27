from datetime import datetime, timedelta

from fastapi import APIRouter, status, Depends

from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.models import Exhibition, ExhibitionRegister
from app.common.consts import UPLOAD_IMAGE
from app.database.schema import Exhibitions, Items, Trades, Profiles, db


router = APIRouter()


@router.post('/exhibition', status_code=status.HTTP_201_CREATED, response_model=Exhibition)
async def create_exhibition(info: ExhibitionRegister, session: Session = Depends(db.session)):
    expire = datetime.now() + timedelta(days=14)

    # TODO: image auto size calculate
    exhibition = Exhibitions.create(session=session, auto_commit=True, item=info.item, trade=info.trade, hall=info.hall,
                                    price=Items.get(id=info.item).price, num=info.num, expire=expire,
                                    max_width=info.max_width, max_height=info.max_height)

    return exhibition


@router.get('/exhibition/{hall}/{num}', status_code=status.HTTP_200_OK, response_model=Exhibition)
async def get_exhibition(hall: int, num: int):
    exhibition = Exhibitions.get(hall=hall, num=num)
    if exhibition is None:
        Exception()

    if exhibition.item is None:
        Exception()

    print(exhibition.item)
    if exhibition.item:
        exhibition.item = Items.get(id=exhibition.item)
        exhibition.item.author = Profiles.get(id=exhibition.item.author).nickname

    if exhibition.trade:
        exhibition.trade = Trades.get(id=exhibition.trade)
        exhibition.trade.owner = Profiles.get(id=exhibition.trade.owner).nickname
    return exhibition


@router.get('/exhibition/image/{hall}/{num}', status_code=status.HTTP_200_OK)
async def get_exhibition_image(hall: int, num: int):
    exhibition = Exhibitions.get(hall=hall, num=num)
    # * 존재 하지 않은 홀
    if exhibition is None:
        return RedirectResponse(url=UPLOAD_IMAGE)

    item = Items.get(id=exhibition.item)

    # * 존재 하지 않은 아이템
    if item is None:
        Exception()

    return RedirectResponse(url=f'https://themestorage.blob.core.windows.net/{item.upload}')

# TODO: 이미지 드로잉 작품 PNG 파일 저장 및 전송 시스템 구축

# TODO: Register Form 연결
# TODO: Trade Form 연결

