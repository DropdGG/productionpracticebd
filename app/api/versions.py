from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.schemas import VersionResponse
from app.repositories.orm_repository import ORMStudentRepository
from app.repositories.native_repository import NativeStudentRepository

router = APIRouter(prefix="/api/versions", tags=["versions"])

def get_repository(use_orm: bool = Query(True)):
    if use_orm:
        return ORMStudentRepository()
    else:
        return NativeStudentRepository()

@router.get("/person/{person_id}", response_model=List[VersionResponse])
async def get_person_versions_api(person_id: int, repo = Depends(get_repository)):
    versions = repo.get_person_versions(person_id)
    if not versions:
        raise HTTPException(404, "Person not found")
    return versions

@router.get("/person/{person_id}/version/{version_number}", response_model=VersionResponse)
async def get_specific_version_api(person_id: int, version_number: int, repo = Depends(get_repository)):
    version = repo.get_version_by_number(person_id, version_number)
    if not version:
        raise HTTPException(404, "Version not found")
    return version