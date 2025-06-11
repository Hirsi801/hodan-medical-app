import frappe
from medical_app.utils.image_utils import format_image_url
from medical_app.utils.response_utils import response_util

@frappe.whitelist()
def get_all_doctors():
    try:
        # Fetch all active healthcare practitioners (doctors)
        doctors = frappe.get_all(
            "Healthcare Practitioner",
            filters={"status": "Active", "hide_dcotor": 0},
            fields=[
                "name", 
                "op_consulting_charge", 
                "department", 
                "image", 
                "services",
                "experience", 
                "available_time"
            ]
        )

        # Check if doctors list is empty
        if not doctors:
            return response_util(
                status="error",
                message="No doctors found in the system.",
                data=None,
                http_status_code=404
            )

        # Format the image URLs using the utility function
        for doctor in doctors:
            doctor["image"] = format_image_url(doctor.get("image"))

        # Return the list of doctors
        return response_util(
            status="success",
            message="Doctors fetched successfully",
            data=doctors,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Doctors Error")
        return response_util(
            status="error",
            message="An error occurred while fetching doctors.",
            error=e,
            data=None,
            http_status_code=500
        )
    
@frappe.whitelist()
def get_doctors_by_department(department):
    try:
        # Fetch healthcare practitioners based on department
        doctors = frappe.get_all(
            "Healthcare Practitioner",
            filters={
                "status": "Active",
                "hide_dcotor": 0,
                "department": department
            },
            fields=["practitioner_name", "op_consulting_charge", "department", "image", "services", "experience", "available_time"]
        )

        # Check if doctors list is empty
        if not doctors:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": "No doctors found in the system.",
                "Data": None
            }
        

        # Format the image URLs if available
        system_host_url = "https://102.68.17.210"  # Replace with your actual host URL
        for doctor in doctors:
            if doctor.image:
                # Ensure image starts with /files/ and add a cache-busting query parameter
                if not doctor.image.startswith('/files/'):
                    doctor.image = f"/files/{doctor.image}"
                doctor.image = f"{system_host_url}{doctor.image}?v={int(time.time())}"
            else:
                doctor.image = None

        # Return the filtered list of doctors
        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Doctors found successfully.",
            "Data": doctors
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Doctors by Department Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while fetching doctors by department.",
            "error": str(e),
            "Data": None
        }


@frappe.whitelist()
def get_all_departments():
    try:
        # Fetch all departments
        departments = frappe.get_all(
            "Medical Department",  # Replace with the exact Doctype name for your departments if it's different
            fields=["name", "department", "department_img"]  # Make sure 'department_img' is a valid field in your Doctype
        )

        # Check if departments list is empty
        if not departments:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": "No departments found in the system.",
                "Data": None
            }

        # Format the image URLs if available
        system_host_url = "https://102.68.17.210"  # Replace with your actual host URL
        for dep in departments:
            if dep.department_img:
                # Ensure image starts with /files/ and add a cache-busting query parameter
                if not dep.department_img.startswith('/files/'):
                    dep.department_img = f"/files/{dep.department_img}"
                dep.department_img = f"{system_host_url}{dep.department_img}?v={int(time.time())}"
            else:
                dep.department_img = None  # If no image, set to None

        # Return the list of departments
        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Departments found successfully.",
            "Data": departments
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Departments Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while fetching departments.",
            "Data": None,
            "error": str(e)
        }
