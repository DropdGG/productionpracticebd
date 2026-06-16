from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Text, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class OrgUnit(Base):
    __tablename__ = 'org_units'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    unit_type = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey('org_units.id'))
    created_at = Column(Date)
    updated_at = Column(Date)
    
    parent = relationship("OrgUnit", remote_side=[id], backref="children")

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20))
    email = Column(String(255), unique=True)
    address = Column(Text)
    created_at = Column(Date)
    current_version_id = Column(Integer, ForeignKey('person_versions.id'))
    is_active = Column(Boolean, default=True)

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), unique=True)
    student_number = Column(String(20), unique=True, nullable=False)
    group_name = Column(String(50), nullable=False)
    org_unit_id = Column(Integer, ForeignKey('org_units.id'))
    enrollment_year = Column(Integer, nullable=False)
    study_form = Column(String(20), default='full-time')
    
    person = relationship("Person")

class Teacher(Base):
    __tablename__ = 'teachers'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), unique=True)
    teacher_number = Column(String(20), unique=True, nullable=False)
    academic_degree = Column(String(100))
    academic_title = Column(String(100))
    position = Column(String(100))
    org_unit_id = Column(Integer, ForeignKey('org_units.id'))
    hire_date = Column(Date, nullable=False)
    
    person = relationship("Person")

class PersonVersion(Base):
    __tablename__ = 'person_versions'
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'))
    version_number = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    changed_at = Column(Date)
    changed_by = Column(String(100))