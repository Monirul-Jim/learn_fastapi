from pydantic import BaseModel,HttpUrl,EmailStr
from datetime import datetime
class Course(BaseModel):
    id:int
    name:str
    instructor:str
    duration:float
    website: HttpUrl

class classResponse(Course):
    id=int
    class Config:
        orm_model=True

class UserCreate(BaseModel):
    email:EmailStr
    password:str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True