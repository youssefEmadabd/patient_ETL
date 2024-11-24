import os
import pandas as pd
from dotenv import load_dotenv

from etl_process.extraction import DataExtractor
from etl_process.transform import DataTransformer
from etl_process.loading import DataLoader

load_dotenv()

DB_CONNECTION_STRING = os.getenv('DB_CONNECTION_STRING')

def extract():
    extractor = DataExtractor(api_url="https://api.fda.gov/drug/label.json?search={}&limit={}", json_file_path="data/Bettina657_Leuschke194_8574d506-b8e9-9e27-e2a5-db0b5d50712f.json")
    extractor.run_extraction_process()
    data_object = {
        "patient": extractor.df_patient.to_dict(orient="records"),
        "medication": extractor.df_medication.to_dict(orient="records"),
        "events": extractor.df_events.to_dict(orient="records")
    }
    return data_object

def transform(**kwargs):
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids="extract")
    data_transformer = DataTransformer(data_dict=data_dict)
    data_transformer.transform()
    data_object = {
        "patient": data_transformer.df_patient.to_dict(orient="records"),
        "medication": data_transformer.df_medication.to_dict(orient="records"),
        "events": data_transformer.df_events.to_dict(orient="records")
    }
    return data_object

def load(**kwargs):
    ti = kwargs['ti']
    data_dict = ti.xcom_pull(task_ids="transform")
    df_patient = pd.DataFrame(data_dict["patient"])
    df_medication = pd.DataFrame(data_dict["medication"])
    df_events = pd.DataFrame(data_dict["events"])

    data_loader = DataLoader(db_url=DB_CONNECTION_STRING, df_patient=df_patient, df_medication=df_medication, df_events=df_events)
    data_loader.load_data_to_sql_database()
    DataTransformer(ti).transform()

if __name__ == "__main__":
    print(0)