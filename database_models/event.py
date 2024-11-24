import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database_models.constants import Base

class Event(Base):
    __tablename__ = 'event'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id = Column(UUID(as_uuid=True), ForeignKey('patient.id'))
    type = Column(String)
    status = Column(String)
    description = Column(String)
    start_date = Column(String, default="")
    end_date = Column(String, default="")

    # Relationships
    patient = relationship("Patient", back_populates="event")
