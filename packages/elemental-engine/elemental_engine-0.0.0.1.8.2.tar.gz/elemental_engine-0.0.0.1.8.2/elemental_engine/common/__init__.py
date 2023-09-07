import os.path
import platform

from fastapi.encoders import jsonable_encoder
from elemental_engine.common.config import possible_encodings
from elemental_engine.handlers.binaries.test import result as test_binaries

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


def get_system_info(test_string: str = test_binaries.initial_string, enable_test_bin=False):
    info = {}
    # Determine CPU architecture
    try:
        if enable_test_bin:
            test_bin_result = test_binaries(test_string)
            info['Binaries Test Result'] = {
                'Complete Result': test_bin_result.result,
                'Test Length': test_bin_result.test_total_length,
                'Encrypt String': test_bin_result.encrypted_string,
                'Decrypt String': test_bin_result.decrypted_string
            }

        info['CPU Architecture'] = platform.machine()
        info['Encoding Test Result'] = {str(e): str(encode(test_string, e)) for e in possible_encodings}
        info['Decoding Test Result'] = {title: str(decode(value.replace("'b", '').replace("'", ''), title)) for
                                        title, value in info['Encoding Test Result'].items()}
        info['Jsonable Encoder Test Result'] = {e: str(json_encode(test_string, e)) for e in possible_encodings}



        # Get system information
        info['Operating System'] = platform.system()
        info['System Architecture'] = platform.architecture()
    except Exception as e:
        info['Last Exception'] = str(e)

    return info
