from data_migrations.utils import fetch_from_json, write_to_json

from data_migrations.charm_migration.utils import CharmPatientAPI
from data_migrations.template_migration.appointment import AppointmentLoaderMixin


class AppointmentLoader(AppointmentLoaderMixin):
    def __init__(self, environment) -> None:
        self.environment = environment
        self.json_file = "PHI/appointments.json"
        self.facilities_json_file = "PHI/facilities.json"
        super().__init__()

    def create_json(self):
        facilities_data = fetch_from_json(self.facilities_json_file)
        facility_ids = [f["facility_id"] for f in facilities_data]
        charm_patient_api = CharmPatientAPI(environment=self.environment)
        charm_patient_api.fetch_appointments(facility_ids, self.json_file)

    def create_facilities_json(self):
        charm_patient_api = CharmPatientAPI(environment=self.environment)
        facilities = charm_patient_api.fetch_facilities()
        write_to_json(self.facilities_json_file, facilities)

    def analyze_appointments(self):
        data = fetch_from_json(self.json_file)
        field_names = [
            "appointment_id",
            "member_id",
            "member_degree",
            "member_specialization",
            "patient_id",
            "facility_id",
            "physician_name",
            "prefix",
            "patient_name",
            "gender",
            "patient_record_id",
            "dob",
            "is_silhouette",
            "blood_group",
            "language",
            "patient_category",
            "preferred_communication",
            "primary_phone",
            "email",
            "home_phone",
            "mobile",
            "work_phone",
            "work_phone_extn",
            "referral_source",
            "referral_specific_source",
            "appointment_start_time_utc",
            "appointment_date",
            "appointment_end_time",
            "appointment_timezone",
            "status_id",
            "status",
            "status_color",
            "appointment_mode",
            "message_to_patient",
            "reason_for_appointment",
            "comment",
            "resource_id",
            "resource_name",
            "encounter_id",
            "is_signed",
            "chart_type",
            "encounter_created_time",
            "encounter_approved_time",
            "is_billing_needed",
            "rcm_push_status",
            "visit_type_id",
            "visit_type",
            "duration",
            "visit_type_color",
            "last_modified_time",
            "time_of_creation",
            "booked_by"
        ]

        for field_name in field_names:
            choices = []
            present = 0
            not_present = 0

            for appointment in data:
                if appointment[field_name]:
                    present += 1
                else:
                    not_present += 1

                if field_name == "visit_type":
                    if appointment[field_name] not in choices:
                        choices.append(appointment[field_name])

            for choice in choices:
                print(choice)

            # print(field_name)
            # print(f"Present: {present}")
            # print(f"Not Present : {not_present}")
            # print("")




if __name__ == "__main__":
    loader = AppointmentLoader("ways2well")
    # loader.create_facilities_json()
    # loader.create_json()
    loader.analyze_appointments()
