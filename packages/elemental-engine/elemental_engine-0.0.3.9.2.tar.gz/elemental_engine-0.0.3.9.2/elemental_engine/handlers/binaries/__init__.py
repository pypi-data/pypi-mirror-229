# Load the C library
import ctypes
import os
import platform, sys
import chardet

system = platform.system()

buffer_size = 4096

binary_root_path = None
default_encoding = sys.getdefaultencoding()

if system == 'Windows':
	encoding = sys.getdefaultencoding()
elif system == 'Linux':
	encoding = 'latin_1'
elif system == 'Darwin':
	encoding = 'ascii'
else:
	encoding = 'utf8'

bin_name = f'{system.lower()}Bin.so'

def set_binary_path():

	binary_path = os.path.join(os.path.dirname(__file__), bin_name)

	if not os.path.isfile(binary_path):
		binary_path = os.path.join('var', 'task', os.path.dirname(__file__), bin_name)

	if not os.path.isfile(binary_path):
		binary_path = f'./elemental_engine/handlers/binaries/{bin_name}'

	if not os.path.isfile(binary_path):
		binary_path = f'./binaries/{bin_name}'

	if not os.path.isfile(binary_path):
		raise Exception(f'Incompatible binary assignment. Please provide a valid binary. Trying to launch {bin_name}')

	return binary_path



def encrypt(value: str):
	cLib = ctypes.CDLL(set_binary_path())
	cEncrypt = cLib.encrypt
	cEncrypt.argtypes = [ctypes.c_char_p]
	cEncrypt.restype = ctypes.c_char_p

	position = 0
	steps = int(len(value) / buffer_size)
	complete_result = []

	for step in range(steps + 1):
		current_step = step + 1
		cEncrypt_bytes = bytes(value[position:current_step * buffer_size], encoding)
		encrypted_value = cEncrypt(cEncrypt_bytes)
		complete_result.append(encrypted_value.decode(encoding))

	return ''.join(complete_result)

def decrypt(value: str):
	cLib = ctypes.CDLL(set_binary_path())
	cDecrypt = cLib.decrypt
	cDecrypt.restype = ctypes.c_char_p
	value_bytes = ctypes.c_char_p(bytes(value, encoding))
	result = cDecrypt(value_bytes)
	return result.decode(encoding)
