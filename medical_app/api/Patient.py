import frappe
from medical_app.utils.response_utils import response_util
from medical_app.utils.image_utils import format_image_url
from datetime import datetime


@frappe.whitelist()
def register_patient(pat_full_name, pat_gender, pat_age, pat_age_type, pat_mobile_number, pat_district):
    try:
        if not pat_full_name:
            return response_util(
                status="error",
                message="Full Name is required.",
                http_status_code=400
            )

        create_doc = frappe.new_doc("Patient")
        
        create_doc.first_name = pat_full_name
        create_doc.sex = pat_gender
        create_doc.p_age = pat_age
        create_doc.age_type = pat_age_type
        create_doc.mobile_no = pat_mobile_number
        create_doc.territory = pat_district
        create_doc.insert()
        frappe.db.commit()

        if create_doc:
            return response_util(
                status="success",
                message="Patient registered successfully.",
                http_status_code=200
            )
        else:
            return response_util(
                status="error",
                message="Patient registration failed.",
                http_status_code=404
            )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Registration Error")
        return response_util(
            status="error",
            message="An error occurred while registering the patient.",
            error=e,
            http_status_code=500
        )

@frappe.whitelist()
def patient_login(mobile_number):
    if not mobile_number:
        return response_util(
            status="error",
            message="Mobile number is required!",
            http_status_code=400
        )

    try:
        patient = frappe.get_value(
            "Patient",
            {"mobile_no": mobile_number},
            "name",
            order_by="creation asc"
        )

        if patient:
            patient_info = frappe.get_doc("Patient", patient)
            
            return response_util(
                status="success",
                message="Login successful",
                data={
                    "patient_id": patient_info.name,
                    "first_name": patient_info.first_name,
                    "mobile": patient_info.mobile_no,
                    "district": patient_info.territory,
                    "age": patient_info.p_age,
                    "Gender": patient_info.sex,
                    "image": format_image_url(patient_info.get('image'))
                },
                http_status_code=200
            )
        else:
            return response_util(
                status="error",
                message="Patient not found with the provided mobile number.",
                http_status_code=404
            )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Login Error")
        return response_util(
            status="error",
            message="An error occurred while logging in",
            error=e,
            http_status_code=500
        )

@frappe.whitelist()
def get_patients_with_same_mobile(mobile_number, doctor_name=None):
    if not mobile_number:
        return response_util(
            status="error",
            message="Mobile number is required.",
            http_status_code=400
        )

    try:
        patients = frappe.get_all(
            "Patient",
            filters={"mobile_no": mobile_number},
            fields=[
                "name", "first_name", "p_age", "image",
                "customer_group", "creation"
            ],
            order_by="creation asc"
        )

        if not patients:
            return response_util(
                status="error",
                message=f"No patients found for mobile number: {mobile_number}",
                http_status_code=404
            )

        enriched_patients = []
        for patient in patients:
            patient_id = patient.get("name")

            # Format image URL
            patient["image"] = format_image_url(patient.get("image"))

            # Ensure required fields exist
            patient["customer_group"] = patient.get("customer_group") or "All Customer Groups"

            # Try to get the latest Fee Validity record
            fee_validity = frappe.get_all(
                "Fee Validity",
                filters={"patient": patient_id},
                fields=["name", "start_date", "valid_till", "status"],
                order_by="creation desc",
                limit_page_length=1
            )

            if fee_validity:
                fee = fee_validity[0]
                patient["followupId"] = fee.get("name")
                patient["followupStartDate"] = fee.get("start_date")
                patient["followupExpirationDate"] = fee.get("valid_till")
                patient["followupStatus"] = fee.get("status")
            else:
                patient["followupId"] = None
                patient["followupStartDate"] = None
                patient["followupExpirationDate"] = None
                patient["followupStatus"] = None

            # Rename fields for frontend consistency
            enriched_patients.append({
                "name": patient["name"],
                "first_name": patient["first_name"],
                "p_age": patient["p_age"],
                "image": patient["image"],
                "customer_group": patient["customer_group"],
                "followupId": patient["followupId"],
                "followupStartDate": patient["followupStartDate"],
                "followupExpirationDate": patient["followupExpirationDate"],
                "followupStatus": patient["followupStatus"]
            })

        return response_util(
            status="success",
            message="Patients found successfully.",
            data=enriched_patients,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Patients with Same Mobile Error")
        return response_util(
            status="error",
            message="An error occurred while retrieving patients.",
            error=e,
            http_status_code=500
        )


@frappe.whitelist()
def get_patient_profile(patient_id):
    try:
        patient_doc = frappe.get_doc("Patient", patient_id)
        
        return response_util(
            status="success",
            message="Patient profile retrieved successfully",
            data={
                "patient_id": patient_doc.name,
                "first_name": patient_doc.first_name,
                "gender": patient_doc.sex,
                "age": patient_doc.p_age,
                "mobile": patient_doc.mobile_no,
                "district": patient_doc.territory,
                "image": format_image_url(patient_doc.get('image'))
            },
            http_status_code=200
        )

    except frappe.DoesNotExistError:
        return response_util(
            status="error",
            message=f"Patient with ID '{patient_id}' does not exist.",
            http_status_code=404
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Patient Profile Error")
        return response_util(
            status="error",
            message="An unexpected error occurred.",
            error=e,
            http_status_code=500
        )

@frappe.whitelist()
def get_districts():
    try:
        districts = frappe.db.get_all("Territory", fields=["territory_name"])
        return response_util(
            status="success",
            message="Districts found successfully.",
            data=districts,
            http_status_code=200
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Districts Error")
        return response_util(
            status="error",
            message="An error occurred while fetching districts.",
            error=e,
            http_status_code=500
        )

@frappe.whitelist()
def get_all_departments():
    try:
        departments = frappe.db.get_all("Department", fields=["name", "department_name"])

        if not departments:
            return response_util(
                status="error",
                message="No departments found in the system.",
                http_status_code=404
            )

        return response_util(
            status="success",
            message="Departments retrieved successfully.",
            data=departments,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Departments Error")
        return response_util(
            status="error",
            message="An error occurred while retrieving departments.",
            error=e,
            http_status_code=500
        )