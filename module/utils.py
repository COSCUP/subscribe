import hmac
import hashlib
from urllib.parse import urlencode

def hmac_encode(code, data):
    args_str = urlencode(sorted(data.items(), key=lambda val: val[0]))
    h = hmac.new(bytes(code, 'utf8'), bytes(args_str, 'utf8'), hashlib.sha256)
    return (h.hexdigest(), args_str)

def hmac_verify(code, hash_str, args_str):
    h = hmac.new(bytes(code, 'utf8'), bytes(args_str, 'utf8'), hashlib.sha256)
    return h.hexdigest() == hash_str
