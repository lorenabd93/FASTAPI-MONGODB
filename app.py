import os
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse 
from fastapi.encoders import jsonable_encoder 
from pydantic import BaseModel, Field, EmailStr 
from bson import ObjectId 
from typing import Optional, List 
import motor.motor_asyncio

app = FastAPI()


MONGODB_URL ='mongodb+srv://lorenabd93:Lorena1993@cluster0.4mgxzhi.mongodb.net/test'

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.misiontic


class PyObjectId(ObjectId):
    @classmethod 
    def __get_validators__(cls):
        yield cls.validate 
          
    @classmethod 
    def validate(cls, v): 
        if not ObjectId.is_valid(v): 
            raise ValueError("Invalid objectid") 
        return ObjectId(v)

    @classmethod 
    def __modify_schema__(cls, field_schema): 
        field_schema.update(type="string")

class StudentModel(BaseModel):
   id: PyObjectId = Field(default_factory=PyObjectId, alias="_id") 
   Nombre: str = Field(...)
   email: EmailStr = Field(...) 
   Curso: str = Field(...) 
   Edad: int = Field(..., le=40)

   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                "Nombre": "Jane Doe",
                "email": "jdoe@example.com",
                "Curso": "Desarrollo de aplicaciones Web",
                "Edad": "23"
           } 
        } 

class UpdateStudentModel(BaseModel): 
   Nombre: Optional[str]
   email: Optional[EmailStr] 
   Curso: Optional[str] 
   Edad: Optional[int]

   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = {
           "example": { 
                "Nombre": "Jane Doe", 
                "email": "jdoe@example.com", 
                "Curso": "Desarrollo de aplicaciones Web", 
                "Edad": "30"
           }  
        }       

@app.post("/", response_description="Add new student",response_model=StudentModel) 
async def create_student(student: StudentModel = Body(...)): 
   student = jsonable_encoder(student) 
   new_student = await db["tripulantes"].insert_one(student) 
   created_student = await db["tripulantes"].find_one({"_id": new_student.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)

@app.get("/", response_description="List all students",response_model=List[StudentModel] )
async def list_students(): 
   students = await db["tripulantes"].find().to_list(1000) 
   return students

@app.get("/{id}", response_description="Get a single student",response_model=StudentModel ) 
async def show_student(id: str): 
    if (student := await db["tripulantes"].find_one({"_id": id})) is not None: 
        return student

    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.put("/{id}", response_description="Update a student", response_model=StudentModel) 
async def update_student(id: str, student: UpdateStudentModel = Body(...)): 
    student = {k: v for k, v in student.dict().items() if v is not None}

    if len(student) >= 1: 
     update_result = await db["tripulantes"].update_one({"_id": id}, {"$set": student})
     
     if update_result.modified_count == 1: 
            if (
                updated_student := await db["tripulantes"].find_one({"_id": id})
            ) is not None:
                return updated_student
        
    if (existing_student := await db["tripulantes"].find_one({"_id": id})) is not None:
         return existing_student
    
    raise HTTPException(status_code=404, detail=f"Student {id} not found")

@app.delete("/{id}", response_description="Delete a student") 
async def delete_student(id: str): 
    delete_result = await db["tripulantes"].delete_one({"_id": id}) 
    
    if delete_result.deleted_count == 1: 
        return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"Student {id} not found")    





