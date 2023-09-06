import secrets
import base58
import hashlib
import datetime
import traceback


def gen_random_sha(length=None):
    """
    Generate a random sha256 string;
    :param length: int, the integer argument to pass to secrets.token_urlsafe()
    :return: str, sha256.
    """
    if length is None:
        length = 36
    milli_date = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
    random_num = f"{secrets.token_urlsafe(length)}:{milli_date}"
    sha256 = base58.b58encode(hashlib.sha256(random_num.encode()).digest())
    string_hash = ''.join(map(chr, sha256))
    return string_hash
