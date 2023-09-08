import os.path
import platform

from fastapi.encoders import jsonable_encoder
from elemental_engine.common.config import possible_encodings
from elemental_engine.handlers.binaries import encrypt, decrypt, buffer_size

# import subprocess

def relative(path):
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), path)


def encode(value, encoding):
    try:
        result = value.encode(encoding)
    except Exception as e:
        result = str(e)

    return result


def decode(value, encoding):
    try:
        result = bytes(value, encoding)
    except Exception as e:
        result = str(e)

    return result


def json_encode(value, encoding):
    try:
        result = jsonable_encoder(value.encode(encoding))
    except UnicodeDecodeError as e:
        result = str(e)

    return result




initial_string = ''.join(['a', 'b', 'c', 'd', 'e', 'f', 'g', ' '] * 64)

class test_encrypter:
    test_length = 100

    def __init__(self, test_string=initial_string):
        self.test_string = test_string
        self.encrypted_string = encrypt(self.test_string)

        self.decrypted_string = decrypt(self.encrypted_string)
        self.test_result = []

        for i in range(self.test_length):
            self.test_result.append({self.decrypted_string == self.test_string})

        self.test_total_length = int(self.test_length * len(self.test_string))
        self.result = False


def get_system_info(test_string: str = initial_string, enable_test_bin=False):
    info = {}
    # Determine CPU architecture
    try:
        if enable_test_bin:
            info['Test String'] = test_string
            test_bin_result = test_encrypter(info['Test String'])
            info['Binaries Test Result'] = {
                'Complete Result': test_bin_result.result,
                'Test Length': test_bin_result.test_total_length,
                'Encrypt String': test_bin_result.encrypted_string,
                #'Decrypt String': test_bin_result.decrypted_string
            }

        info['CPU Architecture'] = platform.machine()
        info['Encoding Test Result'] = {str(e): str(encode(info['Test String'], e)) for e in possible_encodings}
        info['Decoding Test Result'] = {title: str(decode(value.replace("'b", '').replace("'", ''), title)) for
                                        title, value in info['Encoding Test Result'].items()}
        info['Jsonable Encoder Test Result'] = {e: str(json_encode(info['Test String'], e)) for e in possible_encodings}

        # Get system information
        info['Operating System'] = platform.system()
        info['System Architecture'] = platform.architecture()
    except Exception as e:
        info['Last Exception'] = str(e)

    return info
