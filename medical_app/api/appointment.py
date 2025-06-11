
import frappe
from medical_app.utils.response_utils import response_util
from datetime import datetime

@frappe.whitelist()
def create_appointment(PID, doctor_practitioner, 
                    #    doct_amount, 
                       appointment_date,
                       ):
    try:
        # Input validation
        if not all([PID, doctor_practitioner,
                    # doct_amount, 
                    appointment_date]):
            return response_util(
                status="error",
                message="PID, Doctor Practitioner, Amount and Appointment Date are required.",
                data=None,
                http_status_code=400
            )
        
        appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        # Check appointment date is not in the past
        # try:
            # appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        #     if appointment_date_obj < datetime.now().date():
        #         return response_util(
        #             status="error",
        #             message="Appointment date cannot be in the past.",
        #             data=None,
        #             http_status_code=400
        #         )
        # except ValueError:
        #     return response_util(
        #         status="error",
        #         message="Invalid appointment date format. Use YYYY-MM-DD.",
        #         data=None,
        #         http_status_code=400
        #     ) 

        # Check if patient exists
        if not frappe.db.exists("Patient", PID):
            return response_util(
                status="error",
                message=f"Patient with ID {PID} does not exist.",
                data=None,
                http_status_code=404
            )

        # Check if doctor exists
        if not frappe.db.exists("Healthcare Practitioner", doctor_practitioner):
            return response_util(
                status="error",
                message=f"Doctor with ID {doctor_practitioner} does not exist.",
                data=None,
                http_status_code=404
            )
         
        # Get patient's customer group
        customer_group = frappe.db.get_value("Patient", PID, "customer_group")
        
        # Get doctor consultation charge
        doct_amount = frappe.db.get_value("Healthcare Practitioner", doctor_practitioner, "op_consulting_charge")
        
        # Check for valid fee validity (follow-up)
        fee_validity = frappe.get_all(
            "Fee Validity",
            filters={
                "patient": PID,
                "practitioner": doctor_practitioner,
                "status": "Pending"
            },
            fields=["name", "valid_till", "visited", "max_visits"],
            order_by="creation desc",
            limit_page_length=1
        )
        
        original_amount = float(doct_amount)
        payable_amount = original_amount
        appointment_type = "New Patient"  # Default appointment type
        is_follow_up = False
        
        # Priority 1: Check for follow-up (100% free)
        if fee_validity:
            fee_validity = fee_validity[0]
            valid_till = datetime.strptime(str(fee_validity.valid_till), "%Y-%m-%d").date()
            current_date = appointment_date_obj
            
            if current_date <= valid_till and fee_validity.visited < fee_validity.max_visits:
                payable_amount = 0
                appointment_type = "Follow Up"
                is_follow_up = True
                
                # Update fee validity
                frappe.db.set_value("Fee Validity", fee_validity.name, "visited", fee_validity.visited + 1)
                if fee_validity.visited + 1 >= fee_validity.max_visits:
                    frappe.db.set_value("Fee Validity", fee_validity.name, "status", "Completed")
        
        # Priority 2: Apply 50% discount for Membership patients (if not follow-up)
        elif customer_group == "Membership":
            payable_amount = original_amount * 0.5
        
        # Create appointment
        appointment = frappe.new_doc("Que")
        appointment.update({
            "patient": PID,
            "practitioner": doctor_practitioner,
            "date": appointment_date,
            "payable_amount": payable_amount,
            "mode_of_payment": "Cash",
            "cost_center": "Main - HH",
            "appointment_source": "Mobile-App",
            "que_type": appointment_type,
            "follow_up": is_follow_up,
        })
        
        appointment.insert()
        frappe.db.commit()

        return response_util(
            status="success",
            message="Appointment created successfully",
            data={
                "appointment_id": appointment.name,
                "appointment_type": appointment_type,
                "amount_charged": payable_amount,
                "original_amount": original_amount
            },
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Appointment Error")
        return response_util(
            status="error",
            message="An error occurred while creating the appointment.",
            error=str(e),
            data=None,
            http_status_code=500
        )      
        
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
            fields=["name", "patient","patient_name", "practitioner", "payable_amount", "creation", 
                    "appointment_source"
                    ],
            order_by="creation desc"
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
