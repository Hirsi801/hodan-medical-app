import frappe
import re
from frappe.utils import flt
from medical_app.utils.response_utils import response_util
# from erpnext.accounts.party import get_party_account



# @frappe.whitelist()
# def validate_sales_order_for_conversion(sales_order_id=None):
#     try:
#         if not sales_order_id:
#             return response_util(
#                 status="error",
#                 message="sales_order_id parameter is required.",
#                 http_status_code=400
#             )

#         # Fetch Sales Order
#         so_doc = frappe.get_doc("Sales Order", sales_order_id)

#         if so_doc.docstatus != 1:
#             return response_util(
#                 status="error",
#                 message="Only submitted Sales Orders can be converted to Sales Invoices.",
#                 http_status_code=400
#             )

#         if not getattr(so_doc, "ref_practitioner", None):
#             return response_util(
#                 status="error",
#                 message="Sales Order is missing Referring Practitioner which is required in the Sales Invoice.",
#                 http_status_code=400
#             )

#         # Validate item rates
#         for item in so_doc.items:
#             if not item.rate or flt(item.rate) == 0:
#                 return response_util(
#                     status="error",
#                     message=f"Rate cannot be zero for item: {item.item_name} (Row: {item.idx})",
#                     http_status_code=400
#                 )

#         # Check credit limit (simulate invoice to trigger validation)
#         try:
#             si_doc = frappe.new_doc("Sales Invoice")
#             si_doc.customer = so_doc.customer
#             si_doc.due_date = frappe.utils.nowdate()
#             si_doc.selling_price_list = so_doc.selling_price_list
#             si_doc.ignore_pricing_rule = 1
#             si_doc.is_pos = 1
#             si_doc.update_stock = 0
#             si_doc.customer_address = so_doc.customer_address
#             si_doc.shipping_address_name = so_doc.shipping_address_name
#             si_doc.set_posting_time = 1
#             si_doc.posting_date = frappe.utils.nowdate()
#             si_doc.ref_practitioner = so_doc.ref_practitioner
#             si_doc.cost_center = so_doc.get("cost_center") or "Main - HH"

#             for item in so_doc.items:
#                 si_doc.append("items", {
#                     "item_code": item.item_code,
#                     "item_name": item.item_name,
#                     "description": item.description,
#                     "qty": item.qty,
#                     "rate": item.rate,
#                     "uom": item.uom,
#                     "conversion_factor": item.conversion_factor,
#                     "cost_center": "Main - HH",
#                     "so_detail": item.name,
#                     "sales_order": so_doc.name
#                 })

#             # Don't save or submit — just run validations
#             si_doc.run_method("validate")

#         except frappe.ValidationError as ve:
#             message = str(ve)

#             if "credit limit" in message.lower():
#                 return response_util(
#                     status="error",
#                     message="Customer's credit limit has been exceeded. Approval is required before proceeding.",
#                     error=message,
#                     http_status_code=400
#                 )

#             return response_util(
#                 status="error",
#                 message="Validation failed during credit limit check.",
#                 error=message,
#                 http_status_code=400
#             )

#         return response_util(
#             status="success",
#             message="Sales Order is valid for conversion.",
#             data={"sales_order_id": sales_order_id},
#             http_status_code=200
#         )

#     except frappe.DoesNotExistError:
#         return response_util(
#             status="error",
#             message=f"Sales Order {sales_order_id} not found.",
#             http_status_code=404
#         )

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Validate Sales Order for Conversion Error")
#         return response_util(
#             status="error",
#             message="Unexpected error while validating Sales Order.",
#             error=str(e),
#             http_status_code=500
#         )

@frappe.whitelist()
def validate_sales_order_for_conversion(sales_order_id=None):
    try:
        if not sales_order_id:
            return response_util(
                status="error",
                message="sales_order_id parameter is required.",
                http_status_code=400
            )

        # Load Sales Order
        so_doc = frappe.get_doc("Sales Order", sales_order_id)

        if so_doc.docstatus != 1:
            return response_util(
                status="error",
                message="Only submitted Sales Orders can be converted to Sales Invoices.",
                http_status_code=400
            )

        # Validate ref_practitioner
        if not getattr(so_doc, "ref_practitioner", None):
            return response_util(
                status="error",
                message="Sales Order is missing Referring Practitioner which is required in the Sales Invoice.",
                http_status_code=400
            )

        # Validate all item rates are non-zero
        for item in so_doc.items:
            if not item.rate or item.rate == 0:
                return response_util(
                    status="error",
                    message=f"Rate cannot be zero for item: {item.item_name} (Row: {item.idx})",
                    http_status_code=400
                )

        # Create Sales Invoice
        # si_doc = frappe.new_doc("Sales Invoice")
        # si_doc.customer = so_doc.customer
        # si_doc.patient = so_doc.patient
        # si_doc.due_date = frappe.utils.nowdate()
        # si_doc.selling_price_list = so_doc.selling_price_list
        # # si_doc.ignore_pricing_rule = 1
        # si_doc.update_stock = 0
        # si_doc.is_pos = 1
        # si_doc.customer_address = so_doc.customer_address
        # si_doc.shipping_address_name = so_doc.shipping_address_name
        # si_doc.set_posting_time = 1
        # si_doc.posting_date = frappe.utils.nowdate()
        # si_doc.ref_practitioner = so_doc.ref_practitioner
        # si_doc.cost_center = so_doc.get("cost_center") or "Main - HH"

        # for item in so_doc.items:
        #     si_doc.append("items", {
        #         "item_code": item.item_code,
        #         "item_name": item.item_name,
        #         "description": item.description,
        #         "qty": item.qty,
        #         "rate": item.rate,
        #         "uom": item.uom,
        #         "conversion_factor": item.conversion_factor,
        #         "cost_center": so_doc.get("cost_center") or "Main - HH",
        #         "so_detail": item.name,
        #         "sales_order": so_doc.name
        #     })
            
        # si_doc.append("payments", {
        #     "mode_of_payment": "Cash",
        #     "amount": so_doc.rounded_total or so_doc.grand_total,
        # })
        
        # Don't save or submit — just run validations
        # si_doc.run_method("validate")

        return response_util(
            status="success",
            message=f"Sales Invoice created from Sales Order {sales_order_id}",
            # data={"invoice_id": si_doc.name},
            http_status_code=201
        )

    except frappe.ValidationError as ve:
        message = str(ve)

        # Handle credit limit errors with raw HTML
        if "credit limit has been crossed" in message.lower() or "extend the credit limits" in message.lower():
            approvers = []

            # Try to extract all email addresses
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', message)
            names = re.findall(r'<li>(.*?)\s\(', message)

            # Zip them together into name/email objects if match count agrees
            if names and emails and len(names) == len(emails):
                approvers = [{"name": n.strip(), "email": e.strip()} for n, e in zip(names, emails)]
            else:
                approvers = emails or ["Credit approvers not found in message."]

            return response_util(
                status="error",
                message="Customer's credit limit has been exceeded. Approval is required before proceeding.",
                data=approvers,
                error=message,
                http_status_code=400
            )

        # Other validation errors
        return response_util(
            status="error",
            message="Validation error occurred while submitting Sales Invoice.",
            error=message,
            http_status_code=400
        )

    except frappe.DoesNotExistError:
        return response_util(
            status="error",
            message=f"Sales Order {sales_order_id} not found.",
            http_status_code=404
        )

    except Exception as e:
        frappe.errprint(f"Error converting Sales Order to Sales Invoice: {str(e)}")
        return response_util(
            status="error",
            message="Unexpected error while converting Sales Order to Sales Invoice.",
            error=str(e),
            http_status_code=500
        )



@frappe.whitelist()
def convert_sales_order_to_invoice(sales_order_id=None):
    try:
        if not sales_order_id:
            return response_util(
                status="error",
                message="sales_order_id parameter is required.",
                http_status_code=400
            )

        # Load Sales Order
        so_doc = frappe.get_doc("Sales Order", sales_order_id)

        if so_doc.docstatus != 1:
            return response_util(
                status="error",
                message="Only submitted Sales Orders can be converted to Sales Invoices.",
                http_status_code=400
            )

        # Validate ref_practitioner
        if not getattr(so_doc, "ref_practitioner", None):
            return response_util(
                status="error",
                message="Sales Order is missing Referring Practitioner which is required in the Sales Invoice.",
                http_status_code=400
            )

        # Validate all item rates are non-zero
        for item in so_doc.items:
            if not item.rate or item.rate == 0:
                return response_util(
                    status="error",
                    message=f"Rate cannot be zero for item: {item.item_name} (Row: {item.idx})",
                    http_status_code=400
                )

        # Create Sales Invoice
        si_doc = frappe.new_doc("Sales Invoice")
        si_doc.customer = so_doc.customer
        si_doc.patient = so_doc.patient
        si_doc.due_date = frappe.utils.nowdate()
        si_doc.selling_price_list = so_doc.selling_price_list
        # si_doc.ignore_pricing_rule = 1
        si_doc.update_stock = 0
        si_doc.is_pos = 1
        si_doc.customer_address = so_doc.customer_address
        si_doc.shipping_address_name = so_doc.shipping_address_name
        si_doc.set_posting_time = 1
        si_doc.posting_date = frappe.utils.nowdate()
        si_doc.ref_practitioner = so_doc.ref_practitioner
        si_doc.cost_center = so_doc.get("cost_center") or "Main - HH"

        for item in so_doc.items:
            si_doc.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "rate": item.rate,
                "uom": item.uom,
                "conversion_factor": item.conversion_factor,
                "cost_center": so_doc.get("cost_center") or "Main - HH",
                "so_detail": item.name,
                "sales_order": so_doc.name
            })
            
        si_doc.append("payments", {
            "mode_of_payment": "Cash",
            "amount": so_doc.rounded_total or so_doc.grand_total,
        })
        si_doc.insert(ignore_permissions=True)
        si_doc.submit()

        return response_util(
            status="success",
            message=f"Sales Invoice created from Sales Order {sales_order_id}",
            data={"invoice_id": si_doc.name},
            http_status_code=201
        )

    except frappe.ValidationError as ve:
        message = str(ve)

        # Handle credit limit errors with raw HTML
        if "credit limit has been crossed" in message.lower() or "extend the credit limits" in message.lower():
            approvers = []

            # Try to extract all email addresses
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', message)
            names = re.findall(r'<li>(.*?)\s\(', message)

            # Zip them together into name/email objects if match count agrees
            if names and emails and len(names) == len(emails):
                approvers = [{"name": n.strip(), "email": e.strip()} for n, e in zip(names, emails)]
            else:
                approvers = emails or ["Credit approvers not found in message."]

            return response_util(
                status="error",
                message="Customer's credit limit has been exceeded. Approval is required before proceeding.",
                data=approvers,
                error=message,
                http_status_code=400
            )

        # Other validation errors
        return response_util(
            status="error",
            message="Validation error occurred while submitting Sales Invoice.",
            error=message,
            http_status_code=400
        )

    except frappe.DoesNotExistError:
        return response_util(
            status="error",
            message=f"Sales Order {sales_order_id} not found.",
            http_status_code=404
        )

    except Exception as e:
        frappe.errprint(f"Error converting Sales Order to Sales Invoice: {str(e)}")
        return response_util(
            status="error",
            message="Unexpected error while converting Sales Order to Sales Invoice.",
            error=str(e),
            http_status_code=500
        )


@frappe.whitelist()
def get_sales_orders_by_mobile(mobile=None):
    try:
        if not mobile:
            return response_util(
                status="error",
                message="Mobile number is required.",
                http_status_code=400
            )

        # Step 1: Get all patients with this mobile
        patient_records = frappe.get_all(
            "Patient",
            filters={"mobile": mobile},
            fields=["name", "patient_name"]
        )
        if not patient_records:
            return response_util(
                status="error",
                message=f"No patients found for mobile: {mobile}",
                data=[],
                http_status_code=404
            )

        # Create a patient name lookup
        patient_name_map = {p["name"]: p["patient_name"] for p in patient_records}
        patient_ids = list(patient_name_map.keys())

        # Step 2: Get Sales Orders
        sales_orders = frappe.get_all(
            "Sales Order",
            filters={"patient": ["in", patient_ids], "docstatus": 1},
            fields=[
                "name", "transaction_date", "customer", "customer_group", "patient",
                "grand_total", "status", "delivery_date", "contact_mobile"
            ],
            # order_by="transaction_date desc"
            order_by="modified desc"
        )

        # Step 3: Add items + patient_name
        for so in sales_orders:
            # Attach items
            so["items"] = frappe.get_all(
                "Sales Order Item",
                filters={"parent": so["name"]},
                fields=["item_code", "item_name", "qty", "rate", "amount"]
            )

            # Attach patient name
            so["patient_name"] = patient_name_map.get(so["patient"], "")

        return response_util(
            status="success",
            message="Sales Orders retrieved successfully",
            data=sales_orders,
            http_status_code=200
        )

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Get Sales Orders with Items Error")
        return response_util(
            status="error",
            message="Internal Server Error",
            error=str(e),
            http_status_code=500
        )