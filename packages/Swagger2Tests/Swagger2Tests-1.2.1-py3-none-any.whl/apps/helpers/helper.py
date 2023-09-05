import datetime
import random
import string
import hashlib
import json
import logging
from urllib.parse import quote_plus
from faker import Faker


class Helper:

    @staticmethod
    def get_random_choice_from_values(*args):
        return random.choice(args)

    @staticmethod
    def get_random_int(start: int = -100, end: int = 100):
        return random.randint(start, end)

    @classmethod
    def get_random_positive_int(cls, start: int = 1, end: int = 100):
        return cls.get_random_int(start, end)

    @classmethod
    def get_random_negative_int(cls, start: int = -100, end: int = -1):
        return cls.get_random_int(start, end)

    @classmethod
    def get_random_float(cls, start: int = -100, end: int = 100):
        return random.random() * cls.get_random_int(start, end)

    @staticmethod
    def get_random_bool():
        return random.choice([True, False])

    @staticmethod
    def get_null_value():
        return None

    @staticmethod
    def get_random_phone() -> str:
        faker = Faker('zh_CN')
        return faker.phone_number()

    @classmethod
    def get_random_string(cls, min_len: int = 0, max_len: int = 100):
        string_len = cls.get_random_int(min_len, max_len)
        return "".join(
            random.choices(string.ascii_uppercase + string.digits,
                           k=string_len))

    @classmethod
    def get_random_datetime(
        cls,
        result_format: str = "%Y-%m-%d %H:%M:%S",
        min_timestamp: int = 0,
        max_timestamp: int = 1600000000
    ):  # from Unix start time to 09/13/2020 @ 12:26pm (UTC)
        result = cls.get_random_int(min_timestamp, max_timestamp)
        result = datetime.datetime.fromtimestamp(result)
        return result.strftime(result_format)

    @classmethod
    def get_random_password(cls, min_len: int = 8, max_len: int = 25):
        string_len = cls.get_random_int(min_len, max_len)
        return "".join(
            random.choices(string.ascii_uppercase + string.digits +
                           string.punctuation,
                           k=string_len))

    @classmethod
    def get_random_email(cls, min_len: int = 10, max_len: int = 25):
        username_len = cls.get_random_int(min_len, max_len)
        tld_len = cls.get_random_int(2, 5)
        username_len -= tld_len
        domain_len = cls.get_random_int(5, 10)
        username_len -= domain_len
        if any(i <= 0 for i in [tld_len, domain_len, username_len]):
            return cls.get_random_email()
        tld = "".join(random.choices(string.ascii_lowercase, k=tld_len))
        domain = "".join(
            random.choices(string.ascii_uppercase + string.digits,
                           k=domain_len))
        username = "".join(
            random.choices(string.ascii_uppercase + string.digits,
                           k=username_len))
        return f"{ username }@{ domain }.{ tld }"

    @classmethod
    def get_random_ipv4(cls):
        result = cls.get_random_int(0, 255)
        for x in range(3):
            result += "." + cls.get_random_int(0, 255)
        return result

    @classmethod
    def get_random_ipv6(cls):
        result = "".join(random.choices("abcdef" + string.digits, k=4))
        for x in range(7):
            result += ":" + "".join(
                random.choices("abcdef" + string.digits, k=4))
        return result
    
    @staticmethod
    def convert_to_camel_case(string):
        words = string.replace('_', '-').split('-')
        camel_case = words[0] + ''.join(word.capitalize() for word in words[1:])
        return camel_case

    @staticmethod
    def generate_sign(source: dict, secret: str) -> str:
        key_array = sorted(source.keys())
        wait_sign_str = ""

        for k in key_array:
            if k == "sign":
                continue
            if source[k] is not None:
                if isinstance(source[k], dict):
                    source[k] = json.dumps(
                        source[k],
                        separators=(',', ':'))  # remove python因为美观加的空格
                if source[k].strip():
                    wait_sign_str += f"{k}={source[k].strip()}&"

        wait_sign_str += f"key={secret}"
        # logging.info("待签名 urlencode前 %s" % (wait_sign_str))
        wait_sign_str_encoded = quote_plus(
            wait_sign_str)  # 否则会有+和%20的问题，与java不一致
        # logging.info("待签名 urlencode后 %s" % (wait_sign_str_encoded))
        wait_sign_str_encoded_byte = wait_sign_str_encoded.encode('utf-8')
        hash_value = hashlib.sha256(wait_sign_str_encoded_byte).digest()
        encode_str = "".join("{:02x}".format(b) for b in hash_value)

        return encode_str

class RequestInfo(object):
    request_url:str
    request_path:str
    request_body:dict
    request_params:dict
    request_method:str
    
    def __init__(self) -> None:
        self.request_url = None
        self.request_path = None
        self.request_method = None
        self.request_body = {}
        self.request_params = {}