import pytz
import pandas as pd

from etl_process.extraction import DataExtractor

utc = pytz.UTC

class DataTransformer:
    df_patient: pd.DataFrame
    df_medication: pd.DataFrame
    df_events: pd.DataFrame
    
    def __init__(self, data_dict: dict):
        self.df_patient = pd.DataFrame(data_dict["patient"])
        self.df_medication = pd.DataFrame(data_dict["medication"])
        self.df_events = pd.DataFrame(data_dict["events"])
        
    def __safe_tz_localize(self, val):
        try:
            # If the value is already a datetime and not null
            if pd.notnull(val) and isinstance(val, pd.Timestamp):
                # Use tz_convert for tz-aware timestamps
                if val.tzinfo is not None:
                    return val.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # Use tz_localize for tz-naive timestamps
                else:
                    return val.tz_localize("UTC").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # If the value is a string, try to parse it as datetime
            elif isinstance(val, str):
                parsed_date = pd.to_datetime(val, errors="coerce")
                if pd.notnull(parsed_date):
                    # Handle tz-aware strings
                    if parsed_date.tzinfo is not None:
                        return parsed_date.tz_convert("UTC")
                    # Handle tz-naive strings
                    else:
                        return parsed_date.tz_localize("UTC")
            
            # If it's something else (e.g., NaT or invalid), return NaT
            return ""

        except Exception as e:
            print(f"Error localizing value {val}: {e}")
            return ""

    
    def __transform_medications(self):
        self.df_medication.dropna(subset=["medication"], inplace=True)
        valid_patient_ids = set(self.df_patient["id"])
        self.df_medication = self.df_medication[self.df_medication["subject_id"].isin(valid_patient_ids)]
    
    def __transform_events(self):
        self.df_events["description"].fillna("", inplace=True)
        valid_patient_ids = set(self.df_patient["id"])
        self.df_events = self.df_events[self.df_events["subject_id"].isin(valid_patient_ids)]
        self.df_events["start_date"] = self.df_events["start_date"].apply(self.__safe_tz_localize)
        self.df_events["end_date"] = self.df_events["end_date"].apply(self.__safe_tz_localize)
        self.df_events["status"].fillna("in_progress", inplace=True)
    def __transform_patients(self):
        self.df_patient["birth_date"] = self.df_patient["birth_date"].apply(self.__safe_tz_localize)

    def transform(self):
        self.__transform_patients()
        self.__transform_medications()
        self.__transform_events()
        return 
