import json
import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from contextlib import asynccontextmanager

from app.services import UserDAO
from app.db import Session
from app.models import User
from app.settings import settings
from app.schemas import SUser


def load_data_from_json(filename):
    session = Session()

    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(current_dir + "/" + filename, 'r', encoding='utf-8') as file:
            users_data = json.load(file)

        users = [User(**user_data) for user_data in users_data]

        session.add_all(users)
        session.commit()
        print(f"Успешно загружено {len(users)} записей")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при загрузке данных: {str(e)}")
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data_from_json("test_data.json")

app = FastAPI()

# Настройка паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Зависимости для получения текущего пользователя
async def get_current_client(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        else:
            return username
    except JWTError:
        raise credentials_exception


# Создание и проверка JWT токенов
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


# Маршрут для получения токена
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = UserDAO.find_one_or_none(username=form_data.username)
    password_check = False
    if user:
        if pwd_context.verify(form_data.password, user.hashed_password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(data={"sub": form_data.username},
                                           expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# GET /users - Получить всех пользователей (требует аутентификации)
@app.get("/users", response_model=List[SUser])
def get_users(current_user: str = Depends(get_current_client)):
    users = UserDAO.find_all()
    return users


# GET /users/{user_id} - Получить пользователя по ID (требует аутентификации)
@app.get("/users/{user_id}", response_model=SUser)
def get_user(user_id: int, current_user: str = Depends(get_current_client)):
    user = UserDAO.find_one_or_none(id=user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


# POST /users - Создать нового пользователя (требует аутентификации)
@app.post("/users", response_model=SUser)
def create_user(
    new_user: SUser
):
    new_user.hashed_password = pwd_context.encrypt(new_user.hashed_password)
    username = UserDAO.find_one_or_none(username=new_user.username)
    if username:
        raise HTTPException(status_code=404, detail="Username already exist")
    email = UserDAO.find_one_or_none(email=new_user.email)
    if email:
        raise HTTPException(
            status_code=404,
            detail="Email is already registered"
        )
    UserDAO.add_(**new_user.model_dump())
    return new_user


# PUT /users/{user_id} - Обновить пользователя по ID (требует аутентификации)
@app.put("/users/{user_id}", response_model=SUser)
def update_user(user_id: int, updated_user: SUser,
                current_user: str = Depends(get_current_client)):
    user = UserDAO.find_one_or_none(id=user_id)
    if user:
        updated_user.hashed_password = pwd_context.encrypt(
            updated_user.hashed_password
        )
        UserDAO.update_(model_id=user_id, **updated_user.model_dump())
        return updated_user
    raise HTTPException(status_code=404, detail="User not found")


# DELETE /users/{user_id} - Удалить пользователя по ID (требует аутентификации)
@app.delete("/users/{user_id}", response_model=SUser)
def delete_user(user_id: int, current_user: str = Depends(get_current_client)):
    user = UserDAO.find_one_or_none(id=user_id)
    if user:
        UserDAO.delete_(id=user_id)
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Запуск сервера
# http://localhost:8000/openapi.json swagger
# http://localhost:8000/docs портал документации


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
