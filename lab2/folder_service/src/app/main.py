from typing import List, Dict, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Конфигурация JWT (должна совпадать с сервисом авторизации)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

app = FastAPI()

# Имитация хранилища данных в памяти
fake_db: List[Dict] = []
current_id = 1


# Модели Pydantic
class FolderCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FolderResponse(FolderCreate):
    id: int
    user: str


# Настройка авторизации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        else:
            return username
    except JWTError:
        raise credentials_exception


# API Endpoints
@app.get("/folders", response_model=List[FolderResponse])
async def get_user_folders(current_user: int = Depends(get_current_user)):
    user_folders = [folder for folder in fake_db
                    if folder["user"] == current_user]
    return user_folders


@app.post("/folders", response_model=FolderResponse,
          status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderCreate,
    current_user: str = Depends(get_current_user)
):
    global current_id
    if not folder_data.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Folder name cannot be empty"
        )
    new_folder = {
        "id": current_id,
        "user": current_user,
        "name": folder_data.name,
        "description": folder_data.description
    }
    fake_db.append(new_folder)
    current_id += 1
    return new_folder

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
