from typing import Union

from fastapi import FastAPI
from routes import search, sessions, users, tutors  # Changed from app.routes to routes


app = FastAPI(title="GatorGuides API")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


app.include_router(search.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tutors.router, prefix="/api")