from pydantic import BaseModel, Field, validator
from typing import Optional
import uuid


# Pydantic models
# Address
class Address(BaseModel):
    city: Optional[str]=None
    country: Optional[str]=None
    # To validate city and country is filled correctly
    @validator('city', 'country')
    def not_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v

# Student
class Student(BaseModel):
    id: str = Field(default_factory=lambda: f"{uuid.uuid4().hex[:6].upper()}") # unique id for each student of 6 character
    name: Optional[str]=None
    age: Optional[int]=None
    address: Optional[Address]=None
    # To validate name is correct
    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Enter name correctly')
        return v

    # To validate age is correct
    @validator('age')
    def age_positive(cls, v):
        if v <= 0 or v>100:
            raise ValueError('Age must be int the range 0 to 100')
        return v

# Class to return studentid
class StudentId(BaseModel):
    id: str

# Class to return student search
class StudentsResponse(BaseModel):
    name: str
    age: int  

# Class to return student details
class StudentResponse(BaseModel):
    name: str
    age: int
    address: Address      

