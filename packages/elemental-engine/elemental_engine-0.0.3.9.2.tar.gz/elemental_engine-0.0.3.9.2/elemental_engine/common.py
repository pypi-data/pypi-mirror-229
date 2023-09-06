import os.path
import platform
from fastapi.encoders import jsonable_encoder
# import subprocess

possible_encondings = ['ascii',
                       'utf8',
 'cp437',
 'cp737',
 'cp775',
 'cp850',
 'cp852',
 'cp855',
 'cp856',
 'cp857',
 'cp860',
 'cp861',
 'cp862',
 'cp863',
 'cp864',
 'cp865',
 'cp869',
 'cp874',
 'cp1250',
 'cp1251',
 'cp1252',
 'cp1253',
 'cp1254',
 'cp1255',
 'cp1256',
 'cp1257',
 'cp1258',
 'latin_1',
 'iso8859_2',
 'iso8859_3',
 'iso8859_4',
 'iso8859_5',
 'iso8859_6',
 'iso8859_7',
 'iso8859_8',
 'iso8859_9',
 'iso8859_10',
 'iso8859_13',
 'iso8859_14',
 'iso8859_15',
 'koi8_r',
 'koi8_u',
 'mac_cyrillic',
 'mac_greek',
 'mac_iceland',
 'mac_latin2',
 'mac_roman',
 'mac_turkish',
 'utf_7',
 'utf_8']

def relative(path):
    return os.path.join(os.path.dirname(__file__), path)

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


def get_system_info(test_string: str):
    info = {}
    # Determine CPU architecture
    try:
        info['CPU Architecture'] = platform.machine()
        info['Encoding Test Result'] = {str(e): str(encode(test_string, e)) for e in possible_encondings}
        info['Decoding Test Result'] = {title: str(decode(value.replace("'b",'').replace("'", ''), title)) for title, value in info['Encoding Test Result'].items()}
        info['Jsonable Encoder Test Result'] = {e: str(json_encode(test_string, e)) for e in possible_encondings}
    
        # Get system information
        info['Operating System'] = platform.system()
        info['System Architecture'] = platform.architecture()
    except Exception as e:
        info['Last Exception'] = str(e)

    return info
