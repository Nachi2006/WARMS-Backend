import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_RAW_KEY = os.getenv("ENCRYPTION_KEY", "")

def _get_key() -> bytes:
    raw = _RAW_KEY.strip()
    if not raw:
        raise RuntimeError("ENCRYPTION_KEY is not set in environment")
    decoded = base64.urlsafe_b64decode(raw + "==")
    if len(decoded) != 32:
        raise RuntimeError("ENCRYPTION_KEY must decode to exactly 32 bytes for AES-256")
    return decoded

def encrypt_value(plaintext: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    blob = nonce + ciphertext
    return base64.urlsafe_b64encode(blob).decode("utf-8")

def decrypt_value(token: str) -> str:
    key = _get_key()
    aesgcm = AESGCM(key)
    blob = base64.urlsafe_b64decode(token + "==")
    nonce = blob[:12]
    ciphertext = blob[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
