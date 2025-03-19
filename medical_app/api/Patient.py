import frappe
import requests
import time




@frappe.whitelist()
def register_patient(pat_full_name, pat_gender, pat_age,pat_age_type, pat_mobile_number, pat_district):
    try:
        # Convert age to integer (if it's not already an integer)
        if not pat_full_name:
            frappe.response['http_status_code'] = 400
            return {"status": "error", "message": "Full Name is required."}
        # pat_full_name = 'Ibrahim ALI abddala'
        # Create the patient record
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
            frappe.response['http_status_code'] = 200
            return {"status": "success", "msg": "Patient registered successfully.", "Data": None}
        else:
            frappe.response['http_status_code'] = 404
            return {"status": "error", "msg": "Patient registration failed.", "Data": None}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Registration Error")
        frappe.response['http_status_code'] = 500
        return {"status": "error", "msg": "An error occurred while registering the patient.", "Data": None, "error": str(e)}




@frappe.whitelist()
def patient_login(mobile_number):
    if not mobile_number:
        frappe.response['http_status_code'] = 400
        frappe.response['message'] = {"status": "error", "msg": "Mobile number is required!"}
        return frappe.response['message']

    try:
         # Fetch patient ID based on the mobile number
        # patient = frappe.get_value("Patient", {"mobile_no": mobile_number}, "name")
        # Fetch first/earliest patient ID based on the mobile number
        patient = frappe.get_value(
            "Patient",
            {"mobile_no": mobile_number},
            "name",
            order_by="creation asc"  # Order by creation date ascending to get the first registered patient
        )

        if patient:
            # Fetch the patient's details
            patient_info = frappe.get_doc("Patient", patient)

            # Get the profile image URL, if set
            profile_image = patient_info.get('image', None)  # Using get() with default None

            if profile_image:
                # Check if profile image starts with /files/
                if not profile_image.startswith('/files/'):
                    profile_image = f"/files/{profile_image}"

                # Add cache-busting query parameter (timestamp)
                system_host_url = "https://102.68.17.210"  # Use your actual host URL here
                full_image_url = f"{system_host_url}{profile_image}?v={int(time.time())}"
            else:
                full_image_url = None

            frappe.response['http_status_code'] = 200
            frappe.response['message'] = {
                "status": "success",
                "msg": "Login successful",
                "Data": {
                    "patient_id": patient_info.name,
                    "first_name": patient_info.first_name,
                    "mobile": patient_info.mobile_no,
                    "district": patient_info.territory,
                    "age": patient_info.p_age,
                    "Gender": patient_info.sex,
                    "image": full_image_url
                }
            }

            return frappe.response['message']

        else:
            frappe.response['http_status_code'] = 404
            frappe.response['message'] = {"status": "error", "msg": "Patient not found with the provided mobile number."}
            return frappe.response['message']

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Patient Login Error")
        frappe.response['http_status_code'] = 500
        frappe.response['message'] = {"status": "error", "msg": "An error occurred while logging in", "error": str(e)}
        return frappe.response['message']

@frappe.whitelist()
def get_patients_with_same_mobile(mobile_number,doctor_name=None):
    """
    Return all patients (their name and age) who have the same mobile number.
    Example API Call:
      /api/method/medical_app.api.patient.get_patients_with_same_mobile?mobile_number=123456
    """
    if not mobile_number:
        frappe.response['http_status_code'] = 400
        return {
            "status": "error",
            "msg": "Mobile number is required.",
            "Data": None
        }

    try:
        # Get a list of all Patient docs matching the mobile number
        patients = frappe.get_all(
            "Patient",
            filters={"mobile_no": mobile_number},
            fields=["name", "first_name", "p_age", "image", "creation"],
            order_by="creation asc"  # Order by creation date ascending (oldest first)
        )

        # Check if patients list is empty
        if not patients:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": f"No patients found for mobile number: {mobile_number}",
                "Data": None
            }


        # Process image URLs for each patient
        for patient in patients:
            profile_image = patient.get('image')
            if profile_image:
                if not profile_image.startswith('/files/'):
                    profile_image = f"/files/{profile_image}"

                system_host_url = "https://102.68.17.210"
                patient['image'] = f"{system_host_url}{profile_image}?v={int(time.time())}"
            else:
                patient['image'] = None

        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Patients found successfully.",
            "Data": patients
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Patients with Same Mobile Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while retrieving patients.",
            "Data": None,
            "error": str(e)
        }





@frappe.whitelist()
def get_patient_profile(patient_id):
    try:
        # Fetch the Patient document
        patient_doc = frappe.get_doc("Patient", patient_id)

        # Get the profile image URL, if set
        profile_image = patient_doc.get('image', None)  # Using get() with default None

        if profile_image:
            # Check if profile image starts with /files/
            if not profile_image.startswith('/files/'):
                profile_image = f"/files/{profile_image}"

            # Add cache-busting query parameter (timestamp)
            system_host_url = "https://102.68.17.210"  # Use your actual host URL here
            full_image_url = f"{system_host_url}{profile_image}?v={int(time.time())}"
        else:
            full_image_url = None

        # Return patient details along with the image URL
        return {
            "status": "success",
            "msg": "Patient profile retrieved successfully",
            "Data": {
                "patient_id": patient_doc.name,
                "first_name": patient_doc.first_name,
                "gender": patient_doc.sex,
                "age": patient_doc.p_age,
                "mobile_number": patient_doc.mobile_no,
                "district": patient_doc.territory,
                "image": full_image_url
            }
        }

    except frappe.DoesNotExistError:
        # Handle the case where the patient does not exist
        frappe.response['http_status_code'] = 404
        return {
            "status": "error",
            "msg": f"Patient with ID '{patient_id}' does not exist.",
            "Data": None
        }
    except Exception as e:
        # Handle unexpected errors
        frappe.log_error(frappe.get_traceback(), "Get Patient Profile Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An unexpected error occurred.",
            "Data": None,
            "error": str(e)
        }




@frappe.whitelist()
def get_districts():
    # Query all records from the "Territory" doctype and return only the "territory_name" field.
    districts = frappe.db.get_all("Territory", fields=["territory_name"])
    return {
        "status": "success",
        "msg": "Districts found successfully.",
        "Data": districts
    }

@frappe.whitelist()
def get_all_departments():
    try:
        # Query all records from the "Department" doctype
        departments = frappe.db.get_all("Department", fields=["name", "department_name"])

        if not departments:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": "No departments found in the system.",
                "Data": None
            }

        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Departments retrieved successfully.",
            "Data": departments
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Departments Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while retrieving departments.",
            "Data": None,
            "error": str(e)
        }

# api secre  key :  37e28ea0d4de028

# Authorization: token <API_KEY>:<API_SECRET>
