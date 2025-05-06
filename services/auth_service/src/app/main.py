from fastapi import FastAPI, HTTPException, Depends, status, Response, \
    Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta
from passlib.context import CryptContext
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from faker import Faker

from app.services import UserDAO, create_access_token, get_user_id
from app.db import engine
from app.models import Base
from app.settings import settings
from app.schemas import SUser


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    faker = Faker()

    for _ in range(10000):
        await UserDAO.add_(
            username=faker.user_name(),
            email=faker.email(),
            hashed_password=faker.md5(),
            age=faker.random_int(min=18, max=65)
        )

    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/protected")
def get_protected_data(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return {"error": "Токен отсутствует"}
    return {"access_token": access_token}


# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await UserDAO.find_one_or_none(username=form_data.username)
    password_check = False
    if user:
        if pwd_context.verify(form_data.password, user.hashed_password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = await create_access_token(
            data={
                "sub": str(user.id),
                "username": form_data.username
            },
            expires_delta=access_token_expires
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=3600,
            secure=False,
            samesite=None
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.get("/users/", response_model=List[SUser])
async def get_users(user_id: int = Depends(get_user_id)):
    users = await UserDAO.find_all()
    return users


@app.get("/users/{user_id}", response_model=SUser)
async def get_user(
    user_id: int = Depends(get_user_id)
):
    user = await UserDAO.find_one_or_none(id=user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", response_model=SUser)
async def create_user(
    new_user: SUser
):
    new_user.hashed_password = pwd_context.encrypt(new_user.hashed_password)
    username = await UserDAO.find_one_or_none(username=new_user.username)
    if username:
        raise HTTPException(status_code=404, detail="Username already exist")
    email = await UserDAO.find_one_or_none(email=new_user.email)
    if email:
        raise HTTPException(
            status_code=404,
            detail="Email is already registered"
        )
    await UserDAO.add_(**new_user.model_dump())
    return new_user


@app.put("/users/{user_id}", response_model=SUser)
async def update_user(
    updated_user: SUser,
    user_id: int = Depends(get_user_id)
):
    user = await UserDAO.find_one_or_none(id=user_id)
    if user:
        updated_user.hashed_password = pwd_context.encrypt(
            updated_user.hashed_password
        )
        await UserDAO.update_(model_id=user_id, **updated_user.model_dump())
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")


@app.delete("/users/{user_id}", response_model=SUser)
async def delete_user(
    user_id: int = Depends(get_user_id)
):
    user = await UserDAO.find_one_or_none(id=user_id)
    if user:
        await UserDAO.delete_(id=user_id)
        return user
    raise HTTPException(status_code=404, detail="User not found")


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Выход выполнен"}

# Запуск сервера
# http://localhost:8000/openapi.json swagger


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
