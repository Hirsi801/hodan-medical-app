import frappe
import requests
import time

@frappe.whitelist()
def get_all_banners():
 
    try:
        # 1. Fetch all Doctor banners
        banners = frappe.get_all(
            "Doctor banners",
            fields=["name", "banner_image"]
        )

        # Check if banners list is empty
        if not banners:
            frappe.response['http_status_code'] = 404
            return {
                "status": "error",
                "msg": "No banners found in the system.",
                "Data": None
            }
        

        # 2. Base URL for serving images (replace with your actual host)
        system_host_url = "https://102.68.17.210"

        # 3. Format each banner's image URL
        for banner in banners:
            if banner.banner_image:
                # Ensure image starts with /files/
                if not banner.banner_image.startswith('/files/'):
                    banner.banner_image = f"/files/{banner.banner_image}"
                
                # Add cache-busting param
                banner.banner_image = (
                    f"{system_host_url}{banner.banner_image}?v={int(time.time())}"
                )
            else:
                banner.banner_image = None

        # 4. Return the banners data
        frappe.response['http_status_code'] = 200
        return {
            "status": "success",
            "msg": "Banners fetched successfully",
            "Data": banners
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Doctor Banners Error")
        frappe.response['http_status_code'] = 500
        return {
            "status": "error",
            "msg": "An error occurred while fetching doctor banners.",
            "Data": None,
            "error": str(e),
        }
