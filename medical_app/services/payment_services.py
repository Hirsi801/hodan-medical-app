# medical_app/services/payment_services.py
import frappe
import requests
import json
from frappe.utils import now_datetime, now
from datetime import datetime


class PaymentService:
    def __init__(self):
        self.api_url = "https://api.waafipay.net/asm"
        self.api_key = "API-1221796037AHX"
        self.api_user_id = "1007359"
        self.merchant_uid = "M0913615"

    def _save_log(self, patient_id, request_type, payload, response, transaction_id=None, que_id=None):
        """Create one log entry per payment action (init/cancel/commit)."""
        frappe.get_doc({
            "doctype": "Waafi Payment Gateway",
            "patient": patient_id,
            "que": que_id,
            "request_type": request_type,
            "request_payload": json.dumps(payload, indent=2),
            "response_payload": json.dumps(response, indent=2),
            "transaction_id": transaction_id or response.get("params", {}).get("transactionId"),
            "timestamp": now_datetime()
        }).insert(ignore_permissions=True)

    def initiate_preauthorization(self, patient_id, mobile, amount, que_id=None):
        request_id = f"INIT-{datetime.now().strftime('%y%m%d%H%M%S')}-{frappe.generate_hash(length=4)}"
        invoice_id = f"{patient_id}-{frappe.generate_hash(length=6)}"
        reference_id = f"{patient_id}-{frappe.generate_hash(length=6)}"
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Remove +252 and ensure it's just local number like '613656021'
        cleaned_mobile = mobile.replace('+252', '').replace('252', '').lstrip('0')

        payload = {
            "schemaVersion": "1.0",
            "requestId": request_id,
            "timestamp": timestamp,
            "channelName": "WEB",
            "serviceName": "API_PREAUTHORIZE",
            "serviceParams": {
                "merchantUid": self.merchant_uid,
                "apiUserId": self.api_user_id,
                "apiKey": self.api_key,
                "paymentMethod": "MWALLET_ACCOUNT",
                "payerInfo": {
                    "accountNo": cleaned_mobile,
                },
                "transactionInfo": {
                    "referenceId": reference_id,
                    "invoiceId": invoice_id,
                    # "amount": str(int(amount)),  # or str(amount*100) if cents
                    "amount": str(amount),
                    "currency": "USD",
                    "description": f"Appointment Payment for Patient {patient_id}"
                }
            }
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print("Status Code:", response.status_code)
            print("Raw Response:", response.text)

            data = response.json()

            self._save_log(patient_id, "PREAUTHORIZE", payload, data, que_id=que_id)

            if data.get("responseCode") != "2001":
                frappe.throw(data.get("responseMsg", "Payment gateway returned an error"))

            return {
                "status": "success",
                "transaction_id": data["params"]["transactionId"],
                "preauth_code": data["params"]["preauthCode"],
                "cashier_url": data["params"]["cashierURL"]
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Waafi Preauthorization Error")
            frappe.throw(f"Payment failed: {str(e)}")


    def cancel_preauthorization(self, patient_id, transaction_id, mobile, que_id=None):
        """Cancel an existing Waafi preauthorization."""
        request_id = f"CANCEL-{datetime.now().strftime('%y%m%d%H%M%S')}-{frappe.generate_hash(length=4)}"
        payload = {
            "schemaVersion": "1.0",
            "requestId": request_id,
            "timestamp":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "channelName": "WEB",
            "serviceName": "API_PREAUTHORIZE_CANCEL",
            "serviceParams": {
                "merchantUid": self.merchant_uid,
                "apiUserId": self.api_user_id,
                "apiKey": self.api_key,
                "paymentMethod": "MWALLET_ACCOUNT",
                "transactionId": transaction_id,
                "referenceId": f"{transaction_id}-cancel",
                "description": f"Cancel preauth for transaction {transaction_id}",
                "payerInfo": {
                    "accountNo": mobile,
                }
            }
        }

        try:
            response = requests.post(self.api_url, json=payload)
            data = response.json()

            self._save_log(patient_id, "CANCEL", payload, data, transaction_id=transaction_id, que_id=que_id)

            if data.get("responseCode") != "2001":
                frappe.throw(f"Cancel failed: {data.get('responseMsg')}")

            return {
                "status": "cancelled",
                "message": data.get("responseMsg")
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Waafi Cancel Error")
            frappe.throw(f"Cancel failed: {str(e)}")

    def commit_preauthorized_payment(self, patient_id, transaction_id, mobile, que_id=None):
        """Capture (commit) a preauthorized payment."""
        request_id = f"COMMIT-{datetime.now().strftime('%y%m%d%H%M%S')}-{frappe.generate_hash(length=4)}"

        payload = {
            "schemaVersion": "1.0",
            "requestId": request_id,
            "timestamp": now(),
            "channelName": "WEB",
            "serviceName": "API_PREAUTHORIZE_COMMIT",
            "serviceParams": {
                "merchantUid": self.merchant_uid,
                "apiUserId": self.api_user_id,
                "apiKey": self.api_key,
                "paymentMethod": "MWALLET_ACCOUNT",
                "transactionId": transaction_id,
                "referenceId": f"{transaction_id}-commit",
                "description": f"Capture preauth for transaction {transaction_id}",
                "payerInfo": {
                    "accountNo": mobile,
                }
            }
        }

        try:
            response = requests.post(self.api_url, json=payload)
            data = response.json()

            self._save_log(patient_id, "CAPTURE", payload, data, transaction_id=transaction_id, que_id=que_id)

            if data.get("responseCode") != "2001":
                frappe.throw(f"Capture failed: {data.get('responseMsg')}")

            return {
                "status": "captured",
                "message": data.get("responseMsg")
            }

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Waafi Capture Error")
            frappe.throw(f"Capture failed: {str(e)}")


# Example Usage 

# @frappe.whitelist()
# def create_appointment(PID, doctor_practitioner, appointment_date, mobile=None):
#     transaction_id = None
    
#     try:
#         # Basic validations
#         if not all([PID, doctor_practitioner, appointment_date]):
#             raise frappe.ValidationError("PID, Doctor Practitioner, and Appointment Date are required.")

#         appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()

#         if not frappe.db.exists("Patient", PID):
#             raise frappe.DoesNotExistError(f"Patient with ID {PID} does not exist.")

#         if not frappe.db.exists("Healthcare Practitioner", doctor_practitioner):
#             raise frappe.DoesNotExistError(f"Doctor with ID {doctor_practitioner} does not exist.")

#         # Patient and Practitioner data
#         customer_group = frappe.db.get_value("Patient", PID, "customer_group")
#         doct_amount = frappe.db.get_value("Healthcare Practitioner", doctor_practitioner, "op_consulting_charge")
#         original_amount = float(doct_amount or 0)
#         payable_amount = original_amount
#         appointment_type = "New Patient"
#         is_follow_up = False
#         skip_payment = False

#         # Follow-up logic
#         fee_validity = frappe.get_all("Fee Validity", filters={
#             "patient": PID,
#             "practitioner": doctor_practitioner,
#             "status": "Pending",
#         }, fields=["name", "valid_till", "visited", "max_visits"], limit_page_length=1)

#         if fee_validity:
#             fv = fee_validity[0]
#             valid_till = datetime.strptime(str(fv.valid_till), "%Y-%m-%d").date()
#             if appointment_date_obj <= valid_till and fv.visited < fv.max_visits:
#                 payable_amount = 0
#                 appointment_type = "Follow Up"
#                 is_follow_up = True
#                 skip_payment = True

#                 # Update Fee Validity
#                 fee_doc = frappe.get_doc("Fee Validity", fv.name)
#                 fee_doc.visited += 1
#                 if fee_doc.visited >= fee_doc.max_visits:
#                     fee_doc.status = "Completed"
#                 fee_doc.save()

#         elif customer_group == "Membership":
#             payable_amount = original_amount * 0.5

#         # Step 1: Create appointment
#         appointment = frappe.new_doc("Que")
#         appointment.update({
#             "patient": PID,
#             "practitioner": doctor_practitioner,
#             "date": appointment_date,
#             "payable_amount": payable_amount,
#             "mode_of_payment": "Cash",
#             "cost_center": "Main - HH",
#             "appointment_source": "Mobile-App",
#             "que_type": appointment_type,
#             "follow_up": is_follow_up,
#         })
#         appointment.insert()

#         # Step 2: Payment logic (if needed)
#         service = PaymentService()

#         if payable_amount > 0 and not skip_payment:
#             if not mobile:
#                 raise frappe.ValidationError("Mobile number is required for payment.")

#             try:
#                 preauth_result = service.initiate_preauthorization(
#                     patient_id=PID,
#                     mobile=mobile,
#                     # amount=payable_amount,  # Use this in production
#                     amount=0.01,  # For testing
#                     que_id=appointment.name
#                 )
#                 transaction_id = preauth_result.get("transaction_id")

#                 service.commit_preauthorized_payment(
#                     patient_id=PID,
#                     transaction_id=transaction_id,
#                     mobile=mobile,
#                     que_id=appointment.name
#                 )
#             except Exception as payment_error:
#                 # Cancel payment if commit fails
#                 if transaction_id:
#                     try:
#                         service.cancel_preauthorization(
#                             patient_id=PID,
#                             transaction_id=transaction_id,
#                             mobile=mobile,
#                             que_id=appointment.name
#                         )
#                     except Exception as cancel_error:
#                         frappe.log_error(frappe.get_traceback(), "Waafi Cancel on Failure")
#                 raise frappe.ValidationError(f"Payment failed: {payment_error}")

#         # Final response
#         return response_util(
#             status="success",
#             message="Appointment created and payment completed successfully.",
#             data={
#                 "appointment_id": appointment.name,
#                 "appointment_type": appointment_type,
#                 "amount_charged": payable_amount,
#                 "original_amount": original_amount
#             },
#             http_status_code=200
#         )

#     except frappe.ValidationError as ve:
#         return response_util(
#             status="error",
#             message=str(ve),
#             data=None,
#             http_status_code=400
#         )

#     except frappe.DoesNotExistError as dne:
#         return response_util(
#             status="error",
#             message=str(dne),
#             data=None,
#             http_status_code=404
#         )

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), "Create Appointment Error")
#         return response_util(
#             status="error",
#             message="An unexpected error occurred while creating the appointment.",
#             error=e,
#             data=None,
#             http_status_code=500
#         )

   
   
# @frappe.whitelist()
# def proceesPayment():
#     try:
#         que = "QUE25728"
#         service = PaymentService()
#         preauth_result = service.initiate_preauthorization(
#             patient_id="PID-25720",
#             mobile='+252613656021',
#             # amount=payable_amount, # for production
#             amount=0.1, # for testing
#             que_id= que
#         )
        
#         return response_util(
#             status="success",
#             message="Appointment created and payment completed successfully.",
#             data={
#                 "appointment_id": "QUE25728",
#                 "appointment_type": "appointment_type",
#                 "amount_charged": 0.01,
#                 "original_amount": 10,
#                 "result" : preauth_result
#             },
#             http_status_code=200
#         )
#     except Exception as e:
#         return response_util(
#             status="error",
#             message="Failed to create appointment or complete payment.",
#             error=str(e),
#             data=None,
#             http_status_code=500
#         )
           
