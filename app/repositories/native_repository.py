from typing import List, Optional, Dict, Any
from app.database import get_db_connection
from app.repositories.base import StudentRepository, VersionRepository, OrgUnitRepository

class NativeStudentRepository(StudentRepository, VersionRepository):
    def __init__(self):
        self.conn = get_db_connection()
    
    def create_student(self, student_data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO persons (full_name, birth_date, phone, email, address)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                student_data['person']['full_name'],
                student_data['person']['birth_date'],
                student_data['person'].get('phone'),
                student_data['person'].get('email'),
                student_data['person'].get('address')
            ))
            person_id = cursor.fetchone()['id']
            
            cursor.execute("""
                INSERT INTO students (person_id, student_number, group_name, org_unit_id, enrollment_year, study_form)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                person_id,
                student_data['student_number'],
                student_data['group_name'],
                student_data.get('org_unit_id'),
                student_data['enrollment_year'],
                student_data.get('study_form', 'full-time')
            ))
            student_id = cursor.fetchone()['id']
            
            self.conn.commit()
            return student_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_student_by_id(self, student_id: int, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        try:
            if version:
                cursor.execute("""
                    SELECT s.id, s.student_number, s.group_name, s.enrollment_year,
                           p.id as person_id, pv.full_name, pv.birth_date, pv.phone, pv.email, pv.address
                    FROM students s
                    JOIN persons p ON p.id = s.person_id
                    JOIN person_versions pv ON pv.person_id = p.id AND pv.version_number = %s
                    WHERE s.id = %s
                """, (version, student_id))
            else:
                cursor.execute("""
                    SELECT s.id, s.student_number, s.group_name, s.enrollment_year,
                           p.id as person_id, p.full_name, p.birth_date, p.phone, p.email, p.address, p.is_active
                    FROM students s
                    JOIN persons p ON p.id = s.person_id
                    WHERE s.id = %s
                """, (student_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return {
                'id': result['id'],
                'student_number': result['student_number'],
                'group_name': result['group_name'],
                'enrollment_year': result['enrollment_year'],
                'person': {
                    'id': result['person_id'],
                    'full_name': result['full_name'],
                    'birth_date': result['birth_date'],
                    'phone': result.get('phone'),
                    'email': result.get('email'),
                    'address': result.get('address'),
                    'is_active': result.get('is_active', True)
                }
            }
        finally:
            cursor.close()
    
    def get_all_students(self, group_name: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        try:
            query = """
                SELECT s.id, s.student_number, s.group_name, s.enrollment_year, p.full_name
                FROM students s
                JOIN persons p ON p.id = s.person_id
                WHERE p.is_active = TRUE
            """
            params = []
            if group_name:
                query += " AND s.group_name = %s"
                params.append(group_name)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    def update_student(self, student_id: int, update_data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT person_id FROM students WHERE id = %s", (student_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError("Student not found")
            person_id = result['person_id']
            
            cursor.execute("""
                SELECT COALESCE(MAX(version_number), 0) + 1 as next_version
                FROM person_versions
                WHERE person_id = %s
            """, (person_id,))
            next_version = cursor.fetchone()['next_version']
            
            if 'full_name' in update_data:
                cursor.execute("UPDATE persons SET full_name = %s WHERE id = %s", (update_data['full_name'], person_id))
            if 'phone' in update_data:
                cursor.execute("UPDATE persons SET phone = %s WHERE id = %s", (update_data['phone'], person_id))
            if 'email' in update_data:
                cursor.execute("UPDATE persons SET email = %s WHERE id = %s", (update_data['email'], person_id))
            if 'address' in update_data:
                cursor.execute("UPDATE persons SET address = %s WHERE id = %s", (update_data['address'], person_id))
            
            cursor.execute("SELECT full_name, birth_date, phone, email, address FROM persons WHERE id = %s", (person_id,))
            current = cursor.fetchone()
            
            cursor.execute("""
                INSERT INTO person_versions (person_id, version_number, full_name, birth_date, phone, email, address, changed_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (person_id, next_version, current['full_name'], current['birth_date'],
                  current['phone'], current['email'], current['address'], 'api_user'))
            
            if 'group_name' in update_data:
                cursor.execute("UPDATE students SET group_name = %s WHERE id = %s", (update_data['group_name'], student_id))
            
            self.conn.commit()
            return next_version
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def delete_student(self, student_id: int) -> bool:
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT person_id FROM students WHERE id = %s", (student_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            cursor.execute("UPDATE persons SET is_active = FALSE WHERE id = %s", (result['person_id'],))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_person_versions(self, person_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM person_versions
                WHERE person_id = %s
                ORDER BY version_number
            """, (person_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            cursor.close()
    
    def get_version_by_number(self, person_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                SELECT * FROM person_versions
                WHERE person_id = %s AND version_number = %s
            """, (person_id, version_number))
            result = cursor.fetchone()
            return dict(result) if result else None
        finally:
            cursor.close()
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


class NativeOrgUnitRepository(OrgUnitRepository):
    def __init__(self):
        self.conn = get_db_connection()
    
    def create_org_unit(self, unit_data: Dict[str, Any]) -> int:
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO org_units (name, unit_type, parent_id)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (unit_data['name'], unit_data['unit_type'], unit_data.get('parent_id')))
            unit_id = cursor.fetchone()['id']
            self.conn.commit()
            return unit_id
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_org_unit_tree(self, root_id: Optional[int] = None) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        try:
            def build_tree(parent_id=None):
                if parent_id is None:
                    cursor.execute("SELECT id, name, unit_type FROM org_units WHERE parent_id IS NULL")
                else:
                    cursor.execute("SELECT id, name, unit_type FROM org_units WHERE parent_id = %s", (parent_id,))
                units = cursor.fetchall()
                return [{
                    'id': u['id'],
                    'name': u['name'],
                    'unit_type': u['unit_type'],
                    'children': build_tree(u['id'])
                } for u in units]
            
            if root_id:
                cursor.execute("SELECT id, name, unit_type FROM org_units WHERE id = %s", (root_id,))
                root = cursor.fetchone()
                if not root:
                    return {}
                return {
                    'id': root['id'],
                    'name': root['name'],
                    'unit_type': root['unit_type'],
                    'children': build_tree(root['id'])
                }
            else:
                trees = build_tree()
                return {'children': trees} if trees else {}
        finally:
            cursor.close()
    
    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()