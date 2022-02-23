from dataclasses import asdict

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader
from starlette.middleware.authentication import AuthenticationMiddleware

from app.database.conn import Base, db
from app.common.config import conf
from app.middlewares.basic_auth import BasicAuthBackend
from app.router import auth, item, user, trade, order


API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)

app = FastAPI()


def create_app(base: FastAPI) -> FastAPI:
    """
    앱 함수 실행
    :return:
    """
    c = conf()
    conf_dict = asdict(c)
    db.init_app(base, **conf_dict)

    # ! Database 테이블 생성
    Base.metadata.create_all(bind=db.engine)

    # ! MiddleWare 추가
    base.add_middleware(AuthenticationMiddleware, backend=BasicAuthBackend())

    # ! Router 추가
    base.include_router(auth.router, prefix='/api', tags=["Authorization"])
    base.include_router(user.router, prefix='/api', tags=["Account"], dependencies=[Depends(API_KEY_HEADER)])
    base.include_router(item.router, prefix='/api', tags=["Item"], dependencies=[Depends(API_KEY_HEADER)])
    base.include_router(trade.router, prefix='/api', tags=["Trade"], dependencies=[Depends(API_KEY_HEADER)])
    base.include_router(order.router, prefix='/api', tags=["Order"], dependencies=[Depends(API_KEY_HEADER)])
    return base


app = create_app(base=app)


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
