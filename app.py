import os
from fastapi import FastAPI, Body, HTTPException, status 
from fastapi.responses import Response, JSONResponse 
from fastapi.encoders import jsonable_encoder 
from pydantic import BaseModel, Field, EmailStr 
from bson import ObjectId 
from typing import Optional, List 
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class VehiculoModel(BaseModel):
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

class UpdateVehiculoModel(BaseModel): 
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

@app.post("/", response_description="Add new vehiculo",response_model=VehiculoModel) 
async def create_vehiculo(vehiculo: VehiculoModel = Body(...)): 
   vehiculo = jsonable_encoder(vehiculo) 
   new_vehiculo = await db["tripulantes"].insert_one(vehiculo) 
   created_vehiculo = await db["tripulantes"].find_one({"_id": new_vehiculo.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_vehiculo)

@app.get("/", response_description="List all vehiculos",response_model=List[VehiculoModel] )
async def list_vehiculos(): 
   vehiculo = await db["tripulantes"].find().to_list(1000) 
   return vehiculos

@app.get("/{id}", response_description="Get a single vehiculo",response_model=VehiculoModel ) 
async def show_vehiculo(id: str): 
    if (vehiculo := await db["tripulantes"].find_one({"_id": id})) is not None: 
        return vehiculo

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")

@app.put("/{id}", response_description="Update a vehiculo", response_model=VehiculoModel) 
async def update_vehiculo(id: str, vehiculo: UpdateVehiculoModel = Body(...)): 
    vehiculo = {k: v for k, v in vehiculo.dict().items() if v is not None}

    if len(vehiculo) >= 1: 
     update_result = await db["tripulantes"].update_one({"_id": id}, {"$set": vehiculo})
     
     if update_result.modified_count == 1: 
            if (
                updated_vehiculo := await db["tripulantes"].find_one({"_id": id})
            ) is not None:
                return updated_vehiculo
        
    if (existing_vehiculo := await db["tripulantes"].find_one({"_id": id})) is not None:
         return existing_vehiculo
    
    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")

@app.delete("/{id}", response_description="Delete a vehiculo") 
async def delete_vehiculo(id: str): 
    delete_result = await db["tripulantes"].delete_one({"_id": id}) 
    
    if delete_result.deleted_count == 1: 
        return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")    





