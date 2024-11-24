import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from database_models.patient import Patient
from database_models.medication import Medication
from database_models.event import Event
from database_models.constants import Base

class DataLoader:
    __session: Session
    __df_patient: pd.DataFrame
    __df_medication: pd.DataFrame
    __df_events: pd.DataFrame
    
    def __init__(self, db_url: str, df_patient: pd.DataFrame, df_medication: pd.DataFrame, df_events: pd.DataFrame):
        # Create SQLAlchemy Engine
        engine = create_engine(db_url, echo=True)

        # Create tables
        Base.metadata.create_all(engine)

        # Create session
        session_maker = sessionmaker(bind=engine)
        self.__session = session_maker()
        self.__df_patient = df_patient
        self.__df_medication = df_medication
        self.__df_events = df_events

        
    def load_data_to_sql_database(self):
        # Insert Patients
        for _, row in self.__df_patient.iterrows():
            patient = Patient(
                id=row["id"],
                name=row["name"],
                birth_date=row["birth_date"],
                gender=row["gender"],
                address=row["address"],
                phone=row["phone"]
            )
            self.__session.add(patient)

        # Insert Medication Requests
        for _, row in self.__df_medication.iterrows():
            medication_request = Medication(
                id=row["id"],
                subject_id=row["subject_id"],
                status=row["status"],
                intent=row["intent"],
                medication=row["medication"],
                brand_name=row["brand_name"],
                generic_name=row["generic_name"],
                manufacturer=row["manufacturer"],
                active_ingredients=row["active_ingredients"],
                dosage_form=row["dosage_form"],
                route=row["route"],
                warnings=row["warnings"],
                indications_and_usage=row["indications_and_usage"]
            )
            self.__session.add(medication_request)

        # Insert Events
        for _, row in self.__df_events.iterrows():
            event = Event(
                id=row["id"],
                subject_id=row["subject_id"],
                type=row["type"],
                status=row["status"],
                description=row["description"],
                start_date=row["start_date"],
                end_date=row["end_date"]
            )
            self.__session.add(event)

        # Commit transactions
        try:
            self.__session.commit()
            print("Data successfully inserted!")
        except Exception as e:
            self.__session.rollback()
            print("Error inserting data:", e)
