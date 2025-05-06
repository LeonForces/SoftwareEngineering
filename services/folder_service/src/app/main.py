from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from contextlib import asynccontextmanager
from datetime import datetime

from faker import Faker

from app.services import FolderDAO, get_user_id
from app.db import engine
from app.models import Base
from app.schemas import SFolder, SFolderCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    faker = Faker()
    for _ in range(10000):
        await FolderDAO.add_(
            name=faker.word(),
            created_at=faker.date_time(),
            updated_at=faker.date_time(),
            owner_id=faker.random_int(min=1, max=10000)
        )

    yield

app = FastAPI(lifespan=lifespan)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/protected")
async def get_protected_data(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return {"error": "Токен отсутствует"}
    return {"access_token": access_token}


@app.get("/folders/", response_model=list[SFolder])
async def get_folders(
    user_id: int = Depends(get_user_id)
):
    folders = await FolderDAO.find_all()
    return folders


@app.get("/folders/{user_id}", response_model=list[SFolder])
async def get_user_folders(
    user_id: int = Depends(get_user_id)
):
    folders = await FolderDAO.find_all(owner_id=user_id)
    if folders:
        return folders
    raise HTTPException(status_code=404, detail="Folders not found")


@app.post("/folders/", response_model=SFolderCreate)
async def create_folder(
    new_folder: SFolderCreate,
    user_id: int = Depends(get_user_id)
):
    check_folder = await FolderDAO.find_one_or_none(
        name=new_folder.name,
        owner_id=user_id
    )
    if check_folder:
        raise HTTPException(
            status_code=404,
            detail="Folder name already exist"
        )
    folder = {
        "name": new_folder.name,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "owner_id": user_id
    }
    await FolderDAO.add_(**folder)
    return new_folder


@app.put("/folders/{folder_id}", response_model=SFolderCreate)
async def update_folder(
    folder_id: int,
    updated_folder: SFolderCreate,
    user_id: int = Depends(get_user_id)
):
    check_folder = await FolderDAO.find_one_or_none(
        id=folder_id,
        owner_id=user_id
    )
    if check_folder:
        folder = {
            "name": updated_folder.name,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "owner_id": check_folder.owner_id
        }
        await FolderDAO.update_(
            model_id=folder_id, **folder
        )
        return updated_folder
    raise HTTPException(status_code=404, detail="Folder not found")


@app.delete("/folders/{folder_id}", response_model=SFolder)
async def delete_folder(
    folder_id: int,
    user_id: int = Depends(get_user_id)
):
    folder = await FolderDAO.find_one_or_none(
        id=folder_id,
        owner_id=user_id
    )
    if folder:
        await FolderDAO.delete_(id=folder_id)
        return folder
    raise HTTPException(status_code=404, detail="Folder not found")


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
