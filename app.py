from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Path
from pymongo import MongoClient
from dotenv import load_dotenv
from models import Student, StudentId, StudentsResponse, StudentResponse
import os

load_dotenv()
app = FastAPI()

# MongoDB connection
mongodb_uri = os.environ.get("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client.students

# To add student details
@app.post("/students", status_code=201)
async def create_student(student: Student):
    if not student.name:
        raise HTTPException(status_code=400, detail="Name required")
    if not student.age:
        raise HTTPException(status_code=400, detail="Age required")
    if not student.address:
        raise HTTPException(status_code=400, detail="Address required")
    if not student.address.city:
        raise HTTPException(status_code=400, detail="City required")
    if not student.address.country:
        raise HTTPException(status_code=400, detail="Country required")
    
    result = db.student.insert_one(student.dict())
    return StudentId(id=student.id)

# To search students using filters
@app.get("/students", status_code=200)
async def list_students(
    country: Optional[str] = Query(None, description="To apply filter of country."),
    age: Optional[int] = Query(None, description="Only records which have age greater than equal to the provided age should be present in the result.")
):
    filter_query = {}
    if country:
        filter_query["address.country"] = country
    if age:
        filter_query["age"] = {"$gte": age}

    students = db.student.find(filter_query,{"_id": 0, "name": 1, "age": 1})
    return [StudentsResponse(name=student["name"], age=student["age"]) for student in students]

# To search student details using student id
@app.get("/students/{student_id}", status_code=200)
async def fetch_student(student_id: str = Path(..., description="The ID of the student previously created.")):
    student = db.student.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse(**student)

# To update students details
@app.patch("/students/{student_id}", status_code=204)
async def update_student(student_id: str, student: Student):
    existing_student = db.student.find_one({"id": student_id}, {"_id": 0})
    if not existing_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_fields = {}
    if student.name is not None:
        update_fields["name"] = student.name
    if student.age is not None:
        update_fields["age"] = student.age
    if student.address is not None:
        if student.address.city is not None:
            update_fields["address.city"] = student.address.city
        if student.address.country is not None:
            update_fields["address.country"] = student.address.country

    result = db.student.update_one({"id": student_id}, {"$set": update_fields})
    return None  # No content to return

# To delete student details
@app.delete("/students/{student_id}", status_code=200)
async def delete_student(student_id: str):
    result = db.student.delete_one({"id": student_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
