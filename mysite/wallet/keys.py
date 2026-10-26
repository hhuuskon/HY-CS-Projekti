import base64
import secrets

from cryptography.fernet import Fernet
from django.conf import settings


def new_private_key():
    return secrets.token_hex(32)


def new_address():
    return 'HY' + secrets.token_hex(16)


# FLAW 2: private keys are "encrypted" with base64 only
def encrypt(key):
    return base64.b64encode(key.encode()).decode()
    # FIX 2: use real encryption
    # return Fernet(settings.WALLET_KEY).encrypt(key.encode()).decode()


def decrypt(key):
    return base64.b64decode(key.encode()).decode()
    # FIX 2:
    # return Fernet(settings.WALLET_KEY).decrypt(key.encode()).decode()
