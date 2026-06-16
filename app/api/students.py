from fastapi import APIRouter, Depends, HTTPException, Query, Form, Request
from fastapi.responses import RedirectResponse
from typing import List, Optional
from app.schemas import StudentCreate, StudentResponse, StudentUpdate, VersionResponse
from app.repositories.orm_repository import ORMStudentRepository
from app.repositories.native_repository import NativeStudentRepository

router = APIRouter(prefix="/api/students", tags=["students"])

def get_repository(use_orm: bool = Query(True, description="True - ORM, False - Native SQL")):
    if use_orm:
        return ORMStudentRepository()
    else:
        return NativeStudentRepository()

@router.post("/", response_model=dict)
async def create_student_api(student: StudentCreate, repo = Depends(get_repository)):
    student_id = repo.create_student(student.dict())
    return {"id": student_id, "message": "Student created"}

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_api(student_id: int, version: Optional[int] = None, repo = Depends(get_repository)):
    student = repo.get_student_by_id(student_id, version)
    if not student:
        raise HTTPException(404, "Student not found")
    return student

@router.get("/", response_model=List[dict])
async def get_all_students_api(group_name: Optional[str] = None, repo = Depends(get_repository)):
    return repo.get_all_students(group_name)

@router.put("/{student_id}", response_model=dict)
async def update_student_api(student_id: int, update: StudentUpdate, repo = Depends(get_repository)):
    try:
        new_version = repo.update_student(student_id, update.dict(exclude_unset=True))
        return {"message": "Student updated", "new_version": new_version}
    except ValueError:
        raise HTTPException(404, "Student not found")

@router.delete("/{student_id}", response_model=dict)
async def delete_student_api(student_id: int, repo = Depends(get_repository)):
    success = repo.delete_student(student_id)
    if not success:
        raise HTTPException(404, "Student not found")
    return {"message": "Student deleted"}

@router.get("/{student_id}/versions", response_model=List[VersionResponse])
async def get_student_versions_api(student_id: int, repo = Depends(get_repository)):
    student = repo.get_student_by_id(student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    person_id = student['person']['id']
    return repo.get_person_versions(person_id)

@router.get("/{student_id}/versions/{version_number}", response_model=VersionResponse)
async def get_student_version_api(student_id: int, version_number: int, repo = Depends(get_repository)):
    student = repo.get_student_by_id(student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    person_id = student['person']['id']
    version = repo.get_version_by_number(person_id, version_number)
    if not version:
        raise HTTPException(404, "Version not found")
    return version