from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class PersonBase(BaseModel):
    full_name: str
    birth_date: date
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: int
    is_active: bool
    current_version_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class StudentCreate(BaseModel):
    person: PersonCreate
    student_number: str
    group_name: str
    org_unit_id: Optional[int] = None
    enrollment_year: int
    study_form: str = "full-time"

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    group_name: Optional[str] = None

class StudentResponse(BaseModel):
    id: int
    student_number: str
    group_name: str
    enrollment_year: int
    person: PersonResponse
    
    class Config:
        from_attributes = True

class VersionResponse(BaseModel):
    id: int
    version_number: int
    full_name: str
    birth_date: date
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    changed_at: datetime
    changed_by: str

class OrgUnitCreate(BaseModel):
    name: str
    unit_type: str
    parent_id: Optional[int] = None

class OrgUnitResponse(BaseModel):
    id: int
    name: str
    unit_type: str
    parent_id: Optional[int]
    children: List['OrgUnitResponse'] = []

OrgUnitResponse.model_rebuild()