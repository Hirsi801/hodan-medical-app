
import frappe
import requests
import time


# orginal code
@frappe.whitelist()
def create_appointment(PID, doctor_practitioner, doct_amount, appointment_date):
    try:
        create_doc = frappe.new_doc("Que")
        create_doc.payable_amount = doct_amount
        create_doc.doctor_amount = 10
        create_doc.patient = PID
        create_doc.mode_of_payment = "Cash"
        create_doc.practitioner = doctor_practitioner
        create_doc.cost_center = "Main - HH"
        create_doc.appointment_source = 'Mobile App'
        create_doc.date = appointment_date

        create_doc.insert()
        frappe.db.commit()

        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "appointment created Successfully"
        }


    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Appointment Error")
        frappe.response['http_status_code'] = 500
        frappe.response['message'] = {
            "status": "error",
            "msg": "Error while creating appointment",
            "details": str(e)
        }



@frappe.whitelist()
def get_appointments(mobile_no=None):

    # Validate input
    if not mobile_no:
        frappe.response['http_status_code'] = 400
        return {
            "status": "error",
            "msg": "Mobile No is required."
        }

    try:
        # Fetch all appointments (Que docs) linked to this patient
        appointments = frappe.get_all(
            "Que",
            filters={"mobile": mobile_no, "status": ["!=", "Canceled"]},
            fields=["name", "patient","patient_name", "practitioner", "payable_amount", "creation", "appointment_source"]
        )

        # If no appointments found, return 404
        if not appointments:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": f"No appointments found for patient: {mobile_no}",
                "Data": None
            }

        # Return appointments list
        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Appointments retrieved successfully",
            "Data": appointments
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Appointments Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while retrieving appointments.",
            "details": str(e)
        }
