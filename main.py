from fastapi import FastAPI
from pydantic import BaseModel,HttpUrl
app=FastAPI()

#define request body schema
class Course(BaseModel):
    name:str
    instructor:str
    duration:float
    website: HttpUrl

@app.post("/post")
def create_post(post:Course):
    return {"data":post}

@app.get("/")
def main():
    return {"message":"First FastAPI Run Successfully"}