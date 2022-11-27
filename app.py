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

#client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"]) 
MONGODB_URL = 'mongodb+srv://lorenabd93:Lorena1993@cluster0.4mgxzhi.mongodb.net/test'
#MONGODB_URL = "mongodb+srv://dbeetar16:162822@cluster0.u3jbost.mongodb.net/?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.ventavehiculos


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
   Modelo: str = Field("...")
   Marca: EmailStr = Field("...") 
   Kilometraje: int = Field("...") 
   Año: int = Field("...")
   class Config: 
       allow_population_by_field_name = True 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = { 
           "example": { 
                 "Modelo": "Spark",
                "Marca": "Chevrolet",
                "Kilometraje": "0",
                "Año": "2008"
           } 
        } 

class UpdateVehiculoModel(BaseModel): 
   Modelo: Optional[str]
   Marca: Optional[EmailStr] 
   Kilometraje: Optional[str] 
   Año: Optional[int]

   class Config: 
       arbitrary_types_allowed = True 
       json_encoders = {ObjectId: str} 
       schema_extra = {
           "example": { 
                "Modelo": "Spark",
                "Marca": "Chevrolet",
                "Kilometraje": "0",
                "Año": "2008"
           }  
        }       

@app.post("/", response_description="Add new Vehiculo",response_model=VehiculoModel) 
async def create_Vehiculo(Vehiculo: VehiculoModel = Body(...)): 
   Vehiculo = jsonable_encoder(Vehiculo) 
   new_Vehiculo = await db["catalogo"].insert_one(Vehiculo) 
   created_Vehiculo = await db["catalogo"].find_one({"_id": new_Vehiculo.inserted_id}) 
   return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_Vehiculo)

@app.get("/", response_description="List all vehiculos",response_model=List[VehiculoModel] )
async def list_vehiculos(): 
   vehiculos = await db["catalogo"].find().to_list(1000) 
   return vehiculos

@app.get("/{id}", response_description="Get a single vehiculo",response_model=VehiculoModel ) 
async def show_vehiculo(id: str): 
    if (vehiculo := await db["catalogo"].find_one({"_id": id})) is not None: 
        return vehiculo

    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")

@app.put("/{id}", response_description="Update a vehiculo", response_model=VehiculoModel) 
async def update_vehiculo(id: str, vehiculo: UpdateVehiculoModel = Body(...)): 
    vehiculo = {k: v for k, v in vehiculo.dict().items() if v is not None}

    if len(vehiculo) >= 1: 
     update_result = await db["catalogo"].update_one({"_id": id}, {"$set": vehiculo})
     
     if update_result.modified_count == 1: 
            if (
                updated_vehiculo:= await db["catalogo"].find_one({"_id": id})
            ) is not None:
                return updated_vehiculo
        
    if (existing_vehiculo := await db["catalogo"].find_one({"_id": id})) is not None:
         return existing_vehiculo
    
    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")

@app.delete("/{id}", response_description="Delete a vehiculo") 
async def delete_vehiculo(id: str): 
    delete_result = await db["catalogo"].delete_one({"_id": id}) 
    
    if delete_result.deleted_count == 1: 
        return Response(status_code=status.HTTP_204_NO_CONTENT) 
    raise HTTPException(status_code=404, detail=f"Vehiculo {id} not found")    





