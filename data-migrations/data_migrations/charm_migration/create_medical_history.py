from typing import Any

from data_migrations.utils import fetch_from_json, write_to_json
from data_migrations.charm_migration.utils import CharmFHIRAPI, CharmPatientAPI

from data_migrations.template_migration.surgical_history import SurgicalHistoryMixin


class PastSurgicalHistoryLoader(SurgicalHistoryMixin):
    def __init__(self, environment) -> None:
        self.environment = environment
        self.patient_map_file = 'PHI/patient_id_map.json'
        self.patient_map = fetch_from_json(self.patient_map_file)
        self.procedures_json_file = "PHI/medicalhistory_procedures.json"
        self.past_medical_history_json_file = "PHI/medicalhistory_pastmedicalhistory.json"
        self.family_history_json_file = "PHI/medicalhistory_familyhistory.json"
        self.family_history_fhir_json_file = "PHI/medicalhistory_familyhistory_fhir.json"
        self.social_history_json_file = "PHI/medicalhistory_socialhistory.json"
        super().__init__()

    def fetch_past_surgical_history(self):
        patient_ids = list(self.patient_map.keys())
        charm_patient_api = CharmPatientAPI(environment=self.environment)
        # writes to json file
        charm_patient_api.fetch_procedures(patient_ids, self.procedures_json_file)

    def fetch_past_medical_history(self):
        patient_ids = list(self.patient_map.keys())
        charm_patient_api = CharmPatientAPI(environment=self.environment)
        # writes to json file
        charm_patient_api.fetch_pastmedicalhistory(patient_ids, self.past_medical_history_json_file)

    def fetch_family_history(self):
        patient_ids = list(self.patient_map.keys())
        # charm_patient_api = CharmPatientAPI(environment=self.environment)
        # writes to json file
        # charm_patient_api.fetch_family_history(patient_ids, self.family_history_json_file)

        # trying FHIR API since it has codings
        charm_fhir_api = CharmFHIRAPI(environment=self.environment)
        family_history = charm_fhir_api.fetch_family_history()
        write_to_json(self.family_history_fhir_json_file, family_history)

    def fetch_social_history(self):
        patient_ids = list(self.patient_map.keys())
        charm_patient_api = CharmPatientAPI(environment=self.environment)
        # writes to json file
        charm_patient_api.fetch_social_history(patient_ids, self.social_history_json_file)

    def analyze_socialhistory(self):
        data = fetch_from_json(self.social_history_json_file)

        present = 0
        not_present = 0

        for patient_id, social_history in data.items():
            for encounter in social_history["past_encounters"]:
                if encounter["past_family_and_social_history"]:
                    present += 1
                else:
                    not_present += 1

        print(f"Present: {present}")
        print(f"Not Present: {not_present}")

    def analyze_procedures(self):
        data = fetch_from_json(self.procedures_json_file)
        for patient_id, procedure_list in data.items():
            for procedure in procedure_list:
                if procedure["to_date"] and procedure["from_date"] and procedure["to_date"] != procedure["from_date"]:
                    pass

    def analyze_family_history(self):
        twin_counts = {}
        twin_records = []
        data = fetch_from_json(self.family_history_fhir_json_file)
        for history in data:
            twin_coding_found = False
            for coding in history["resource"]["relationship"]["coding"]:
                if 'twin' in coding["display"].lower():
                    if coding["display"].lower() in twin_counts:
                        twin_counts[coding["display"].lower()] += 1
                    else:
                        twin_counts[coding["display"].lower()] = 1
                    if not twin_coding_found:
                        twin_coding_found = True
            if twin_coding_found:
                twin_records.append(history)

        write_to_json("twin_records.txt", twin_records)

        print(twin_counts)


if __name__ == "__main__":
    loader = PastSurgicalHistoryLoader("ways2well")

    # fetched:
    # loader.fetch_past_surgical_history()
    # loader.fetch_past_medical_history()
    # loader.fetch_family_history()
    # loader.fetch_social_history()

    # loader.analyze_socialhistory()
    # loader.analyze_procedures()
    loader.analyze_family_history()
