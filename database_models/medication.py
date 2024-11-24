import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database_models.constants import Base

class Medication(Base):
    __tablename__ = 'medication'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey('patient.id'))
    status = Column(String)
    intent = Column(String)
    medication = Column(String)
    brand_name = Column(String)
    generic_name = Column(String)
    manufacturer = Column(String)
    active_ingredients = Column(String)
    dosage_form = Column(String)
    route = Column(String)
    warnings = Column(String)
    indications_and_usage = Column(String)

    # Relationships
    patient = relationship("Patient", back_populates="medication")
