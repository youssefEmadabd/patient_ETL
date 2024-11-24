import uuid
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database_models.constants import Base


# Patient Model
class Patient(Base):
    __tablename__ = 'patient'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    birth_date = Column(DateTime)
    gender = Column(String)
    address = Column(String)
    phone = Column(String)

    # Relationships
    medication = relationship("Medication", back_populates="patient")
    event = relationship("Event", back_populates="patient")

