from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class StudentRepository(ABC):
    @abstractmethod
    def create_student(self, student_data: Dict[str, Any]) -> int:
        pass
    
    @abstractmethod
    def get_student_by_id(self, student_id: int, version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_all_students(self, group_name: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update_student(self, student_id: int, update_data: Dict[str, Any]) -> int:
        pass
    
    @abstractmethod
    def delete_student(self, student_id: int) -> bool:
        pass

class VersionRepository(ABC):
    @abstractmethod
    def get_person_versions(self, person_id: int) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_version_by_number(self, person_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        pass

class OrgUnitRepository(ABC):
    @abstractmethod
    def create_org_unit(self, unit_data: Dict[str, Any]) -> int:
        pass
    
    @abstractmethod
    def get_org_unit_tree(self, root_id: Optional[int] = None) -> Dict[str, Any]:
        pass