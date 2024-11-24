import json
import pandas as pd
import requests
import re

class DataExtractor:
    df_patient: pd.DataFrame = None
    df_medication: pd.DataFrame = None
    df_events: pd.DataFrame = None
    __json_file_path: str
    __api_url: str
    
    def __init__(self, json_file_path: str, api_url: str) -> None:
        self.__json_file_path = json_file_path
        self.__api_url = api_url
    
    def clean_description(self, text):
        if isinstance(text, str):
            return re.sub(r"[^a-zA-Z0-9\s]", "", text)
        return text

    def __extract_from_json(self, json_data) -> None:
        # Extract entries from the Bundle
        entries = json_data.get("entry", [])

        # Extract patient personal information
        patient_data = []
        medication_requests = []
        events = []

        for entry in entries:
            resource = entry.get("resource", {})
            resource_type = resource.get("resourceType")

            if resource_type == "Patient":
                patient_info = {
                    "id": resource.get("id"),
                    "name": " ".join(resource.get("name", [{}])[0].get("given", []) + [resource.get("name", [{}])[0].get("family", "")]),
                    "birth_date": resource.get("birthDate"),
                    "gender": resource.get("gender"),
                    "address": ", ".join(resource.get("address", [{}])[0].get("line", [])) + " " +
                            resource.get("address", [{}])[0].get("city", ""),
                    "phone": resource.get("telecom", [{}])[0].get("value")
                }
                patient_data.append(patient_info)

            elif resource_type == "MedicationRequest":
                subject_id = resource.get("subject", {}).get("reference")
                if subject_id:
                    medication_info = {
                        "id": resource.get("id"),
                        "subject_id": subject_id.replace("urn:uuid:", ""),
                        "status": resource.get("status"),
                        "intent": resource.get("intent"),
                        "medication": resource.get("medicationCodeableConcept", {}).get("text"),
                    }
                    medication_requests.append(medication_info)

            elif resource_type in ["Encounter", "Condition", "DiagnosticReport"]:
                subject_id = resource.get("subject", {}).get("reference")
                if subject_id:
                    event_info = {
                        "id": resource.get("id"),
                        "subject_id": subject_id.replace("urn:uuid:", ""),
                        "type": resource_type,
                        "status": resource.get("status"),
                        "description": resource.get("code", {}).get("text"),
                        "start_date": resource.get("period", {}).get("start"),
                        "end_date": resource.get("period", {}).get("end"),
                    }
                    events.append(event_info)

        # Create DataFrames
        self.df_patient = pd.DataFrame(patient_data)
        self.df_medication = pd.DataFrame(medication_requests)
        self.df_events = pd.DataFrame(events)
    
    def __extract_and_merge_medication_data_from_api(self) -> None:
        self.df_medication["medication"] = self.df_medication["medication"].apply(self.clean_description)
        medication_info_list = []
        self.df_medication["brand_name"] = ""
        self.df_medication["generic_name"] = ""
        self.df_medication["manufacturer"] = ""
        self.df_medication["active_ingredients"] = ""
        self.df_medication["dosage_form"] = ""
        self.df_medication["route"] = ""
        self.df_medication["warnings"] = ""
        self.df_medication["indications_and_usage"] = ""
        for index, row in self.df_medication.iterrows():
            if row["medication"]:
                response = requests.get(self.__api_url.format(row["medication"], 1), headers={}, data={})
                if response.status_code == 200:
                    data = response.json()
                    data:dict = data["results"][0]
                    join_str: str = ", "
                    fda_data = data.get("openfda",{})
                    self.df_medication.at[index, "brand_name"] = join_str.join(fda_data.get("brand_name", []))
                    self.df_medication.at[index, "generic_name"] =  join_str.join(fda_data.get("generic_name", []))
                    self.df_medication.at[index, "manufacturer"] =  join_str.join(fda_data.get("manufacturer_name", []))
                    self.df_medication.at[index, "active_ingredients"] =  join_str.join(data.get("active_ingredient", []))
                    self.df_medication.at[index, "dosage_form"] =  join_str.join(data.get("dosage_and_administration", []))
                    self.df_medication.at[index, "route"] =  join_str.join(fda_data.get("route", []))
                    self.df_medication.at[index, "warnings"] =  join_str.join(data.get("warnings", []))
                    self.df_medication.at[index, "indications_and_usage"] =  join_str.join(data.get("indications_and_usage", []))
                else:
                    print(f"Failed to fetch medication data for medication ID: {row['id']}")
                    print(f"Error message: {response.text}")
    
    def __transform_data_frames_to_json_format(self) -> dict:
        parsed_data = {
            "patient": self.df_patient.to_dict(orient="records"),
            "medication": self.df_medication.to_dict(orient="records"),
            "events": self.df_events.to_dict(orient="records")
        }
    def run_extraction_process(self) -> None:
        # Load the JSON file
        with open(self.__json_file_path, 'r') as f:
            data = json.load(f)
            
        # Extract data from the JSON
        self.__extract_from_json(data)
        self.__extract_and_merge_medication_data_from_api()
        return self.__transform_data_frames_to_json_format()