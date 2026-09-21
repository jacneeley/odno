'''base64 decode'''
from base64 import b64decode

def decode(encoded_str:str) -> str:
    '''decode using ascii encoding and base64 encryption'''
    b64_bytes=encoded_str.encode("ascii")

    decoded_bytes = b64decode(b64_bytes)
    return decoded_bytes.decode("ascii")
