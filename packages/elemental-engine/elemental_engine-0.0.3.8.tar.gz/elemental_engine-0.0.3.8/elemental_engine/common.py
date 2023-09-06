import os.path
import platform
from fastapi.encoders import jsonable_encoder
# import subprocess

possible_encondings = [
    'ascii',
    'utf-8',
    'utf-16',
    'utf-32',
    'iso-8859-1',
    'iso-8859-15',
    'cp1252',
    'cp437',
    'cp850',
    'latin_1',
    'windows-1250',
    'windows-1254',
    'iso-2022-jp',
    'iso-8859-7'
]

def relative(path):
    return os.path.join(os.path.dirname(__file__), path)

def get_system_info(test_string: str):
    info = {}
    # Determine CPU architecture
    info['CPU Architecture'] = platform.machine()
    info['Encoding Test Result'] = {e: test_string.encode(e) for e in possible_encondings}
    info['Decoding Test Result'] = {title: bytes(value, title) for title, value in info['Encoding Test Result'].items()}
    info['Jsonable Encoder Test Result'] = {e: jsonable_encoder(test_string).encode(e) for e in possible_encondings}

    # Get system information
    info['Operating System'] = platform.system()
    info['System Architecture'] = platform.architecture()

    return info
