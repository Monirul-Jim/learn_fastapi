from fastapi import FastAPI,Depends,Request,status,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel,HttpUrl
from . import models
from sqlalchemy.orm import Session
from . database import engine,get_db
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import DataError
from typing import List
app=FastAPI()
models.Base.metadata.create_all(bind=engine)
#define request body schema
class Course(BaseModel):
    id:int
    name:str
    instructor:str
    duration:float
    website: HttpUrl


@app.get("/")
def main():
    return {"message":"First FastAPI Run Successfully"}

@app.get("/test")
def course(db:Session=Depends(get_db)):
    return {"message":"successfully run this app"}

@app.post("/course")
def create_post(course:Course,db:Session=Depends(get_db)):
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


@app.get('/courses',response_model=List[Course])
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