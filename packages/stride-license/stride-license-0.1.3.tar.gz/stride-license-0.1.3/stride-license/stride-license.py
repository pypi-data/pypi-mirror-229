import json
import base64
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken, InvalidSignature



def decode_license(license_key: str, secret_key: str) -> dict:
    try:
        cipher_suite = Fernet(secret_key)
        # decoded_bytes = bytes.fromhex(license_key)
        decoded_text = base64.urlsafe_b64decode(license_key.encode('utf-8'))
        decrypted_text = cipher_suite.decrypt(decoded_text).decode('utf-8')
        return json.loads(decrypted_text)
    except InvalidToken or InvalidSignature:
        return {'error': True, 'message': 'invalid token'}


def get_license_status(license_key: str, secret_key: str):
    data = decode_license(license_key, secret_key)
    if not "expiry_date" in data:
        return 'Invalid'
    expiry_date = datetime.fromisoformat(data['expiry_date'])
    current_date = datetime.now()
    if expiry_date > current_date:
        return 'Active'
    return 'Expired'

