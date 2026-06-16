from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional
import os

from app.repositories.orm_repository import ORMStudentRepository, ORMOrgUnitRepository
from app.repositories.native_repository import NativeStudentRepository, NativeOrgUnitRepository

app = FastAPI(title="Student Management System", description="Система учета студентов", version="1.0.0")

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

def get_repositories(mode: str):
    if mode == 'orm':
        return ORMStudentRepository(), ORMOrgUnitRepository()
    else:
        return NativeStudentRepository(), NativeOrgUnitRepository()

@app.get("/")
async def index(
    request: Request,
    mode: str = "orm",
    group_filter: Optional[str] = None,
    create_message: Optional[str] = None,
    create_message_type: str = "success",
    update_message: Optional[str] = None,
    update_message_type: str = "success"
):
    student_repo, _ = get_repositories(mode)
    students = student_repo.get_all_students(group_filter if group_filter else None)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": mode,
        "students": students,
        "group_filter": group_filter,
        "create_message": create_message,
        "create_message_type": create_message_type,
        "update_message": update_message,
        "update_message_type": update_message_type,
        "selected_student": None,
        "versions": None,
        "current_version": None,
        "org_tree": None
    })

@app.get("/students/{student_id}")
async def student_detail(
    request: Request,
    student_id: int,
    mode: str = "orm"
):
    student_repo, _ = get_repositories(mode)
    
    student = student_repo.get_student_by_id(student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    
    person_id = student['person']['id']
    versions = student_repo.get_person_versions(person_id)
    current_version = student['person'].get('current_version_id')
    
    all_students = student_repo.get_all_students()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": mode,
        "students": all_students,
        "selected_student": student,
        "versions": versions,
        "current_version": current_version,
        "group_filter": None,
        "org_tree": None
    })

@app.get("/students/{student_id}/version/{version_number}")
async def student_version(
    request: Request,
    student_id: int,
    version_number: int,
    mode: str = "orm"
):
    student_repo, _ = get_repositories(mode)
    
    student = student_repo.get_student_by_id(student_id, version_number)
    if not student:
        raise HTTPException(404, "Student or version not found")
    
    student['is_version'] = True
    student['version_number'] = version_number
    
    all_students = student_repo.get_all_students()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": mode,
        "students": all_students,
        "selected_student": student,
        "versions": student_repo.get_person_versions(student['person']['id']),
        "current_version": version_number,
        "group_filter": None,
        "org_tree": None
    })

@app.post("/students/create")
async def create_student(
    full_name: str = Form(...),
    birth_date: str = Form(...),
    student_number: str = Form(...),
    group_name: str = Form(...),
    enrollment_year: int = Form(...),
    org_unit_id: Optional[int] = Form(None),
    mode: str = Form("orm")
):
    student_repo, _ = get_repositories(mode)
    
    try:
        student_data = {
            "person": {
                "full_name": full_name,
                "birth_date": birth_date,
                "phone": None,
                "email": None,
                "address": None
            },
            "student_number": student_number,
            "group_name": group_name,
            "org_unit_id": org_unit_id,
            "enrollment_year": enrollment_year,
            "study_form": "full-time"
        }
        student_repo.create_student(student_data)
        return RedirectResponse(url=f"/?mode={mode}&create_message=Студент+создан&create_message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/?mode={mode}&create_message=Ошибка:+{str(e)}&create_message_type=error", status_code=303)

@app.post("/students/{student_id}/update")
async def update_student(
    student_id: int,
    new_name: str = Form(...),
    mode: str = Form("orm")
):
    student_repo, _ = get_repositories(mode)
    
    try:
        new_version = student_repo.update_student(student_id, {"full_name": new_name})
        return RedirectResponse(
            url=f"/students/{student_id}?mode={mode}&update_message=Обновлено!+Новая+версия+{new_version}&update_message_type=success",
            status_code=303
        )
    except Exception as e:
        return RedirectResponse(
            url=f"/students/{student_id}?mode={mode}&update_message=Ошибка:+{str(e)}&update_message_type=error",
            status_code=303
        )

@app.post("/students/{student_id}/delete")
async def delete_student(
    student_id: int,
    mode: str = Form("orm")
):
    student_repo, _ = get_repositories(mode)
    
    try:
        student_repo.delete_student(student_id)
        return RedirectResponse(url=f"/?mode={mode}&create_message=Студент+удален&create_message_type=success", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/?mode={mode}&create_message=Ошибка:+{str(e)}&create_message_type=error", status_code=303)

@app.get("/org-tree")
async def org_tree(
    request: Request,
    mode: str = "orm"
):
    _, org_repo = get_repositories(mode)
    student_repo, _ = get_repositories(mode)
    
    tree_data = org_repo.get_org_unit_tree()
    students = student_repo.get_all_students()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "mode": mode,
        "students": students,
        "org_tree": tree_data.get('children', []),
        "group_filter": None,
        "selected_student": None,
        "versions": None,
        "current_version": None
    })

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)