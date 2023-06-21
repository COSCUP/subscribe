''' Utils '''
import hmac
import hashlib
from urllib.parse import urlencode


def hmac_encode(code: str, data: dict[str, str]) -> tuple[str, str]:
    ''' HMAC Encode '''
    args_str = urlencode(sorted(data.items(), key=lambda val: val[0]))
    hmac_obj = hmac.new(bytes(code, 'utf8'), bytes(
        args_str, 'utf8'), hashlib.sha256)
    return (hmac_obj.hexdigest(), args_str)


def hmac_verify(code: str, hash_str: str, args_str: str) -> bool:
    ''' Verify HMAC '''
    hmac_obj = hmac.new(bytes(code, 'utf8'), bytes(
        args_str, 'utf8'), hashlib.sha256)
    return hmac_obj.hexdigest() == hash_str
