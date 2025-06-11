import frappe
import time
from medical_app.utils.image_utils import format_image_url
from medical_app.utils.response_utils import response_util

@frappe.whitelist()
def get_all_banners():
    try:
        # 1. Fetch all Doctor banners
        banners = frappe.get_all(
            "Doctor banners",
            fields=["name", "banner_image", "banner_type"]
        )

        # Check if banners list is empty
        if not banners:
            return response_util(
                status="error",
                message="No banners found in the system.",
                data=None,
                http_status_code=404
            )

        # 2. Format each banner's image URL using the utility function
        for banner in banners:
            banner["banner_image"] = format_image_url(banner.get("banner_image"))

        # 3. Return the banners data using the response utility
        return response_util(
            status="success",
            message="Banners fetched successfully",
            data=banners,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get All Doctor Banners Error")
        return response_util(
            status="error",
            message="An error occurred while fetching doctor banners.",
            data=None,
            error=e,
            http_status_code=500
        )