from pymongo import MongoClient
from fastapi import FastAPI, Depends, Request, HTTPException
from contextlib import asynccontextmanager
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

from faker import Faker

from app.settings import settings
from app.schemas import SEmail
from app.services import get_username

domain = "@mymail.ru"

URI = f"mongodb://{settings.MONGO_USER}:{settings.MONGO_PASS}" + \
    "@mongo-emails:27017"
client = MongoClient(URI)
db = client['leonforce']
collection = db['emails']


@asynccontextmanager
async def lifespan(app: FastAPI):
    collection.drop()
    collection.create_index([("sender", 1)])

    faker = Faker()

    for _ in range(10000):
        email = {
            "sender": faker.email(),
            "recipient": faker.email(),
            "header": faker.word(),
            "description": faker.text(),
            "created_at": faker.date_time()
        }
        collection.insert_one(email)

    yield

    client.close()

app = FastAPI(lifespan=lifespan)


@app.get("/protected")
def get_protected_data(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return {"error": "Токен отсутствует"}
    return {"access_token": access_token}


@app.get("/emails/")
def get_all_emails(
    username: str = Depends(get_username)
):
    result = collection.find().limit(20)

    emails = []
    for doc in result:
        doc["_id"] = str(doc["_id"])
        emails.append(doc)

    return emails


@app.post("/user/emails/")
def create_email(
    email: SEmail,
    username: str = Depends(get_username)
):
    email_data = email.model_dump()
    email_data["sender"] = username + domain
    email_data["created_at"] = datetime.now()
    insert_result = collection.insert_one(email_data)
    return {"email_id": str(insert_result.inserted_id)}


@app.get("/user/emails/")
def get_emails(
    username: str = Depends(get_username)
):
    result = collection.find({"sender": username + domain})

    emails = []
    for doc in result:
        doc["_id"] = str(doc["_id"])
        emails.append(doc)

    return emails


@app.put("/user/emails/")
def update_email(
    new_email: SEmail,
    email_id: str,
    username: str = Depends(get_username)
):
    try:
        update_data = new_email.model_dump()
        update_data["updated_at"] = datetime.now()

        try:
            obj_id = ObjectId(email_id)
        except InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid email ID format"
            )
        result = collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Email not updated"
            )
        return {"modified_count": result.modified_count}
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid email id"
        )


@app.delete("/user/emails/")
def delete_email(
    email_id: str,
    username: str = Depends(get_username)
):
    try:
        obj_id = ObjectId(email_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid email ID format")

    email = collection.find_one(
        {"_id": obj_id}
    )
    if not email:
        raise HTTPException(
            status_code=404,
            detail="Incorrect email id"
        )
    if email["sender"] == username + domain:
        collection.delete_one(
            {"_id": obj_id}
        )
        return {"message": "Email deleted"}
    else:
        raise HTTPException(
            status_code=404,
            detail="Email can not be deleted"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
