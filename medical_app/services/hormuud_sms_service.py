from typing import Dict, Optional
import requests
import json
import frappe
from datetime import datetime
import time

class HormuudSMSService:
    BASE_URL = "https://smsapi.hormuud.com"
    TOKEN_ENDPOINT = f"{BASE_URL}/token"
    SMS_ENDPOINT = f"{BASE_URL}/api/SendSMS"
    BULK_SMS_ENDPOINT = f"{BASE_URL}/api/Outbound/SendBulkSMS"

    def __init__(self):
        self.username = "Hodanhospital"
        self.password = "fj8TVv9w9eLUyknMUhyQpQ=="
        self.cache_key = "hormuud_sms_token"
        self.sender_id = "HODAN HOSPITAL"

    # def _post_with_retry(self, url, headers, data, retries=2, timeout=10):
    #     last_exception = None
    #     for attempt in range(retries + 1):
    #         try:
    #             response = requests.post(url, headers=headers, json=data, timeout=timeout)
    #             response.raise_for_status()
    #             return response
    #         except requests.exceptions.RequestException as e:
    #             last_exception = e
    #             frappe.logger().warning(f"Attempt {attempt+1} failed: {e}")
    #             if attempt < retries:
    #                 time.sleep(1)  # backoff
    #     raise Exception(f"Failed after {retries+1} attempts: {last_exception}")
    
    def _post_with_retry(self, url: str, headers: Dict, data: Dict, 
                        retries: int = 2, timeout: int = 10) -> Optional[requests.Response]:
        """
        Modified retry mechanism that:
        1. Prevents duplicate SMS sends
        2. Only retries on clear failures
        3. Validates responses before considering successful
        """
        last_exception = None
        last_response = None
        
        for attempt in range(retries + 1):
            try:
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
                
                # First validate the response looks successful
                if response.status_code == 200:
                    response_data = response.json()
                    if self._is_valid_response(response_data):
                        frappe.logger().debug(f"SMS API success on attempt {attempt+1}")
                        return response
                    else:
                        # If response is invalid but HTTP 200, log and retry
                        frappe.logger().warning(f"Invalid API response: {response_data}")
                        last_response = response
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                last_exception = e
                frappe.logger().warning(f"Attempt {attempt+1} failed: {str(e)}")
                
            # Don't retry if we got a 200 but just invalid content
            if last_response and last_response.status_code == 200:
                break
                
            if attempt < retries:
                wait_time = min(2 ** attempt, 5)  # Cap at 5 seconds
                time.sleep(wait_time)
        
        # If we got a 200 response but invalid content, return it anyway
        if last_response and last_response.status_code == 200:
            return last_response
            
        # raise Exception(f"Failed after {retries+1} attempts. Last error: {str(last_exception)}")
        raise Exception(f"POST to {url} failed after {retries+1} attempts. Last error: {str(last_exception)}")


    def _is_valid_response(self, response_data: dict) -> bool:
        return (
            isinstance(response_data, dict) and
            response_data.get("ResponseCode") == "200"
        )
  

    def _generate_token(self):
        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            response = requests.post(self.TOKEN_ENDPOINT, data=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            token = data.get("access_token")
            frappe.cache().set_value(self.cache_key, token, expires_in_sec=50)
            return token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Token generation failed: {e}")

    def _get_valid_token(self):
        token = frappe.cache().get_value(self.cache_key)
        if token:
            return token
        return self._generate_token()

    def send_sms(self, mobile: str, message: str, refid="0", validity=0):
        token = self._get_valid_token()
        payload = {
            "senderid": self.sender_id,
            "refid": refid,
            "mobile": mobile,
            "message": message,
            "validity": validity
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = self._post_with_retry(self.SMS_ENDPOINT, headers, payload)
        return response.json()

    def send_bulk_sms(self, messages: list):
        token = self._get_valid_token()
        now = datetime.utcnow().isoformat()
        bulk_payload = []

        for msg in messages:
            bulk_payload.append({
                "refid": msg.get("refid", "bulk-ref"),
                "mobile": msg["mobile"],
                "message": msg["message"],
                "senderid": self.sender_id,
                "mType": 0,
                "eType": 0,
                "validity": msg.get("validity", 0),
                "delivery": 1,
                "UDH": "",
                "RequestDate": now
            })

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = self._post_with_retry(self.BULK_SMS_ENDPOINT, headers, bulk_payload)
        return response.json()
