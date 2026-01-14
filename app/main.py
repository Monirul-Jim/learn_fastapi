from fastapi import FastAPI,Depends
from pydantic import BaseModel,HttpUrl
from . import models
from sqlalchemy.orm import session
from . database import engine,get_db
app=FastAPI()
models.Base.metadata.create_all(bind=engine)
#define request body schema
class Course(BaseModel):
    name:str
    instructor:str
    duration:float
    website: HttpUrl


@app.get("/")
def main():
    return {"message":"First FastAPI Run Successfully"}

@app.get("/test")
def course(db:session=Depends(get_db)):
    return {"message":"successfully run this app"}

@app.post("/post")
def create_post(post:Course):
    pass
