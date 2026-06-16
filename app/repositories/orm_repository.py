from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Optional, Dict, Any

from app.models_orm import Person, Student, Teacher, PersonVersion, OrgUnit
from app.repositories.base import StudentRepository, VersionRepository, OrgUnitRepository
from app.config import config

class ORMStudentRepository(StudentRepository, VersionRepository):
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_student(self, student_data: Dict[str, Any]) -> int:
        session = self.SessionLocal()
        try:
            person = Person(
                full_name=student_data['person']['full_name'],
                birth_date=student_data['person']['birth_date'],
                phone=student_data['person'].get('phone'),
                email=student_data['person'].get('email'),
                address=student_data['person'].get('address')
            )
            session.add(person)
            session.flush()
            
            student = Student(
                person_id=person.id,
                student_number=student_data['student_number'],
                group_name=student_data['group_name'],
                org_unit_id=student_data.get('org_unit_id'),
                enrollment_year=student_data['enrollment_year'],
                study_form=student_data.get('study_form', 'full-time')
            )
            session.add(student)
            session.commit()
            return student.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_student_by_id(self, student_id: int, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        session = self.SessionLocal()
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return None
            
            if version:
                person_version = session.query(PersonVersion).filter(
                    PersonVersion.person_id == student.person_id,
                    PersonVersion.version_number == version
                ).first()
                if not person_version:
                    return None
                person_data = {
                    'id': student.person_id,
                    'full_name': person_version.full_name,
                    'birth_date': person_version.birth_date,
                    'phone': person_version.phone,
                    'email': person_version.email,
                    'address': person_version.address,
                    'is_active': True
                }
            else:
                person = session.query(Person).filter(Person.id == student.person_id).first()
                person_data = {
                    'id': person.id,
                    'full_name': person.full_name,
                    'birth_date': person.birth_date,
                    'phone': person.phone,
                    'email': person.email,
                    'address': person.address,
                    'is_active': person.is_active
                }
            
            return {
                'id': student.id,
                'student_number': student.student_number,
                'group_name': student.group_name,
                'enrollment_year': student.enrollment_year,
                'person': person_data
            }
        finally:
            session.close()
    
    def get_all_students(self, group_name: Optional[str] = None) -> List[Dict[str, Any]]:
        session = self.SessionLocal()
        try:
            query = session.query(Student)
            if group_name:
                query = query.filter(Student.group_name == group_name)
            
            students = query.all()
            result = []
            for s in students:
                person = session.query(Person).filter(Person.id == s.person_id).first()
                # ✅ ДОБАВИТЬ ПРОВЕРКУ is_active
                if person and person.is_active:  # ← ЭТО КЛЮЧЕВОЕ!
                    result.append({
                        'id': s.id,
                        'student_number': s.student_number,
                        'group_name': s.group_name,
                        'full_name': person.full_name,
                        'enrollment_year': s.enrollment_year
                    })
            return result
        finally:
            session.close()
            
    def update_student(self, student_id: int, update_data: Dict[str, Any]) -> int:
        session = self.SessionLocal()
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise ValueError("Student not found")
            
            person = session.query(Person).filter(Person.id == student.person_id).first()
            
            if 'full_name' in update_data:
                person.full_name = update_data['full_name']
            if 'phone' in update_data:
                person.phone = update_data['phone']
            if 'email' in update_data:
                person.email = update_data['email']
            if 'address' in update_data:
                person.address = update_data['address']
            if 'group_name' in update_data:
                student.group_name = update_data['group_name']
            
            session.commit()
            
            new_version = session.query(PersonVersion).filter(
                PersonVersion.person_id == person.id
            ).order_by(PersonVersion.version_number.desc()).first()
            
            return new_version.version_number if new_version else 1
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_student(self, student_id: int) -> bool:
        session = self.SessionLocal()
        try:
            student = session.query(Student).filter(Student.id == student_id).first()
            if not student:
                return False
            
            person = session.query(Person).filter(Person.id == student.person_id).first()
            person.is_active = False
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_person_versions(self, person_id: int) -> List[Dict[str, Any]]:
        session = self.SessionLocal()
        try:
            versions = session.query(PersonVersion).filter(
                PersonVersion.person_id == person_id
            ).order_by(PersonVersion.version_number).all()
            
            return [{
                'id': v.id,
                'version_number': v.version_number,
                'full_name': v.full_name,
                'birth_date': v.birth_date,
                'phone': v.phone,
                'email': v.email,
                'address': v.address,
                'changed_at': v.changed_at,
                'changed_by': v.changed_by
            } for v in versions]
        finally:
            session.close()
    
    def get_version_by_number(self, person_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        session = self.SessionLocal()
        try:
            version = session.query(PersonVersion).filter(
                PersonVersion.person_id == person_id,
                PersonVersion.version_number == version_number
            ).first()
            
            if not version:
                return None
            
            return {
                'id': version.id,
                'version_number': version.version_number,
                'full_name': version.full_name,
                'birth_date': version.birth_date,
                'phone': version.phone,
                'email': version.email,
                'address': version.address,
                'changed_at': version.changed_at,
                'changed_by': version.changed_by
            }
        finally:
            session.close()


class ORMOrgUnitRepository(OrgUnitRepository):
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_org_unit(self, unit_data: Dict[str, Any]) -> int:
        session = self.SessionLocal()
        try:
            unit = OrgUnit(
                name=unit_data['name'],
                unit_type=unit_data['unit_type'],
                parent_id=unit_data.get('parent_id')
            )
            session.add(unit)
            session.commit()
            return unit.id
        finally:
            session.close()
    
    def get_org_unit_tree(self, root_id: Optional[int] = None) -> Dict[str, Any]:
        session = self.SessionLocal()
        try:
            def build_tree(parent_id=None):
                query = session.query(OrgUnit)
                if parent_id is None:
                    query = query.filter(OrgUnit.parent_id.is_(None))
                else:
                    query = query.filter(OrgUnit.parent_id == parent_id)
                
                units = query.all()
                return [{
                    'id': u.id,
                    'name': u.name,
                    'unit_type': u.unit_type,
                    'children': build_tree(u.id)
                } for u in units]
            
            if root_id:
                root = session.query(OrgUnit).filter(OrgUnit.id == root_id).first()
                if not root:
                    return {}
                return {
                    'id': root.id,
                    'name': root.name,
                    'unit_type': root.unit_type,
                    'children': build_tree(root.id)
                }
            else:
                trees = build_tree()
                return {'children': trees} if trees else {}
        finally:
            session.close()