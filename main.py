from fastapi import FastAPI
from pydantic import BaseModel,HttpUrl
import psycopg2
from pydantic_settings import BaseSettings,SettingsConfigDict
from psycopg2.extras import RealDictCursor
import time

class Settings(BaseSettings):
    db_host:str
    db_name:str
    db_user:str
    db_password:str
    model_config=SettingsConfigDict(env_file=".env")
settings=Settings()
while True:
    try:
        conn=psycopg2.connect(host=settings.db_host,database=settings.db_name,user=settings.db_user,password=settings.db_password,ursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Connection successfully")
        break;
    except Exception as error:
        print("Datebase connection Failed")
        print("Error",error)
        time.sleep(2)


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