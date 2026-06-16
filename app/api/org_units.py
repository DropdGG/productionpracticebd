from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.schemas import OrgUnitCreate, OrgUnitResponse
from app.repositories.orm_repository import ORMOrgUnitRepository
from app.repositories.native_repository import NativeOrgUnitRepository

router = APIRouter(prefix="/api/org-units", tags=["org_units"])

def get_repository(use_orm: bool = Query(True)):
    if use_orm:
        return ORMOrgUnitRepository()
    else:
        return NativeOrgUnitRepository()

@router.post("/", response_model=dict)
async def create_org_unit_api(unit: OrgUnitCreate, repo = Depends(get_repository)):
    unit_id = repo.create_org_unit(unit.dict())
    return {"id": unit_id, "message": "Org unit created"}

@router.get("/tree", response_model=dict)
async def get_org_tree_api(root_id: Optional[int] = None, repo = Depends(get_repository)):
    return repo.get_org_unit_tree(root_id)