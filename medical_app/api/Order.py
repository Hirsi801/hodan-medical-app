import frappe
from medical_app.utils.response_utils import response_util



@frappe.whitelist(allow_guest=False)
def get_sales_orders_by_mobile(mobile=None):
    """
    Fetches orders filtered by mobile number with items
    Returns data structured to match Flutter OrderModel
    """
    try:
        if not mobile:
            return response_util(
                status="error",
                message="Mobile number is required",
                http_status_code=400
            )
        
        # Get orders with field names that match Flutter model
        orders = frappe.get_all(
            "Sales Order",
            filters={"contact_mobile": mobile},
            fields=[
                "name",          # Matches OrderModel
                "transaction_date",
                "customer",
                "customer_group",
                "patient",
                "patient_name",
                "delivery_date",
                "status",
                "contact_mobile",
                "grand_total"
            ],
            order_by="creation desc"
        )

        if not orders:
            return response_util(
                status="success",
                message="No orders found",
                data=[],
                http_status_code=200
            )

        # Get items for each order
        for order in orders:
            items = frappe.get_all(
                "Sales Order Item",
                filters={"parent": order["name"]},
                fields=[
                    "item_code",
                    "item_name",
                    "qty",
                    "rate",
                    "amount",
                    "image"
                ]
            )
            
            order["items"] = items

        return response_util(
            status="success",
            message="Orders fetched successfully",
            data=orders,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Orders Error")
        return response_util(
            status="error",
            message="Failed to fetch orders",
            error=str(e),
            http_status_code=500
        )