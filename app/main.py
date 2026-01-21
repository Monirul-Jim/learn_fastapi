from fastapi import FastAPI,Depends,Request,status,HTTPException,Response,APIRouter
from fastapi.responses import JSONResponse

from . import models ,schemas
from sqlalchemy.orm import Session
from . database import engine,get_db
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError
from typing import List
from .helper import utils
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone

app=FastAPI()
models.Base.metadata.create_all(bind=engine)
#define request body schema

# router=APIRouter(prefix="/defineurl")
@app.get("/")
def main():
    return {"message":"First FastAPI Run Successfully"}

@app.get("/test")
def course(db:Session=Depends(get_db)):
    return {"message":"successfully run this app"}



SECRET_KEY = "your_ultra_secret_key_here" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
def create_access_token(data: dict):
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/users/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/course",response_model=schemas.classResponse)
def create_post(course:schemas.Course,db:Session=Depends(get_db)):
    new_course=models.Course(
        name=course.name,
        instructor=course.instructor,
        duration=course.duration,
        website=str(course.website)
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {
        "success":"Success",
        "message":"Data Created Successfully",
        "status":201

    }


@app.get('/courses',response_model=List[schemas.Course])
def get_all_courses(db:Session=Depends(get_db)):
    courses=db.query(models.Course).all()
    return courses



@app.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    # Look for the course with the matching ID
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    
    # If not found, return 404
    if not course:
        raise HTTPException(
            status_code=404, 
            detail=f"Course with ID {course_id} was not found"
        )
        
    return {
        "success": "Success",
        "data": course
    }

@app.put("/course/{id}")
def updated_course(id:int,updated_course:schemas.Course,db:Session=Depends(get_db)):
    course_qeury=db.query(models.Course).filter(models.Course==id)
    course=course_qeury.first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"course with this {id} does not exist")
    update_data=updated_course.model_dump()
    update_data['website']=str(update_data["website"])
    course_qeury.update(update_data,synchronize_session=False)
    db.commit()
    db.refresh(course)


@app.post("/users",status_code=status.HTTP_201_CREATED)
def create_user(user:schemas.UserCreate,db:Session=Depends(get_db)):
    hashed_password=utils.hash_password(user.password)
    user.password=hashed_password


    new_user=models.User(**user.dict())
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User with this email exists")
    return new_user

@app.get("/users",response_model=List[schemas.UserCreate])
def get_user(db:Session=Depends(get_db)):
    users=db.query(models.User).all()
    return users

@app.post("/login")
def login(user_credentials: schemas.UserCreate, response: Response, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()

    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    # Generate tokens
    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    # Set Refresh Token in HTTP-Only Cookie
    response.set_cookie(
        key="refresh_token", 
        value=refresh_token, 
        httponly=True,   # Prevents JavaScript from reading the cookie (Secure)
        max_age=7 * 24 * 60 * 60, # 7 days in seconds
        expires=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False     # Set to True in Production (requires HTTPS)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/refresh")
def refresh(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    # Logic to verify token and issue a new access_token here...
    return {"access_token": "new_token_here"}
@app.exception_handler(404)
async def custom_404_handler(request:Request,__):
    return JSONResponse(
        status_code=404,
        content={
            "error":"API Not Found !",
            "message":"The requested resource does not exist",
            "path":request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # Identify the field name and the type of error
        field = error.get("loc")[-1]
        error_type = error.get("type")
        
        # Customize message for float parsing errors
        if error_type == "float_parsing":
            message = f"The field '{field}' must be a number (float), but you provided a string that couldn't be converted."
        else:
            message = error.get("msg")
            
        errors.append({
            "field": field,
            "message": message
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Failed", "errors": errors},
    )


@app.exception_handler(DataError)
async def sqlalchemy_data_error_handler(request: Request, exc: DataError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Database Error",
            "message": "The data provided does not match the database format (e.g., sending text to a number column)."
        }
    )