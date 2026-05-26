
import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_bytes = private_key.private_numbers().private_value.to_bytes(32, byteorder='big')
    
    # Public key in uncompressed format (0x04 + X + Y)
    public_numbers = public_key.public_numbers()
    x = public_numbers.x.to_bytes(32, byteorder='big')
    y = public_numbers.y.to_bytes(32, byteorder='big')
    public_bytes = b'\x04' + x + y

    private_base64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').strip('=')
    public_base64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').strip('=')

    return public_base64, private_base64

if __name__ == "__main__":
    pub, priv = generate_vapid_keys()
    print(f"VAPID_PUBLIC_KEY={pub}")
    print(f"VAPID_PRIVATE_KEY={priv}")
