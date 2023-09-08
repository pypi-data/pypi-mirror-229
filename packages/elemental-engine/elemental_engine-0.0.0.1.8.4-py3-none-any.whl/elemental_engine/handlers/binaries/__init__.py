# Load the C library
import ctypes
import os
import platform, sys, psutil
import chardet

system = platform.system()
ram_info = psutil.virtual_memory()
buffer_size = int((ram_info.total / 1024 / 1024 / 1024)) - 2

binary_root_path = None
default_encoding = sys.getdefaultencoding()

if system == 'Windows':
	bin_ext = '.dll'
	encoding = sys.getdefaultencoding()
elif system == 'Linux':
	bin_ext = '.so'
	encoding = 'utf8'
elif system == 'Darwin':
	bin_ext = '.dylib'
	encoding = 'ascii'
else:
	bin_ext = '.so'
	encoding = 'utf8'

bin_name = f'bin{bin_ext}'

def set_binary_path():
	valid_paths = []
	possible_paths = [
		os.path.join(os.path.dirname(__file__), bin_name),
		os.path.join('var', 'task', 'elemental_engine', 'handlers', 'binaries', bin_name),
		f'./elemental_engine/handlers/binaries/{bin_name}',
		f'./binaries/{bin_name}'
	]

	for e in possible_paths:
		if os.path.isfile(e):
			try:
				ctypes.cdll.LoadLibrary(e)
				valid_paths.append(e)
			except:
				pass

	if not any(valid_paths):
		raise Exception(f'No valid path for binaries found in possible locations: {possible_paths}')

	return valid_paths[0]

bin_path = set_binary_path()

def encrypt(value: str, enc=encoding, debug=False):
	current_position = 0
	total_index_range = 0
	steps = int(len(value) / buffer_size)
	current_step = int()
	if steps < 1:
		steps = 1
	complete_result = []

	for step in range(steps+1):
		cLib = ctypes.CDLL(bin_path)
		current_step += 1
		cEncrypt = cLib.encrypt
		cEncrypt.argtypes = [ctypes.c_char_p]
		cEncrypt.restype = ctypes.c_char_p
		cEncrypt_bytes = str.encode(value[current_position:(current_step * buffer_size)])
		total_index_range += ((current_step * buffer_size))-current_position
		if debug:
			print(f"Indexing from: {current_position} to {(current_step * buffer_size)} indexing range: {((current_step * buffer_size))-current_position}")

		try:
			encrypted_value = cEncrypt(
				bytes(cEncrypt_bytes)
			).decode(enc)
		except:
			continue

		current_position = (current_step * buffer_size)-1
		complete_result.append(encrypted_value)

	if debug:
		print(f"Total indexing length: {len(value)}, processed amount: {total_index_range}" )


	return ''.join(complete_result)


def decrypt(value: str):
	cLib = ctypes.CDLL(bin_path)
	cDecrypt = cLib.decrypt
	cDecrypt.restype = ctypes.c_char_p
	value_bytes = ctypes.c_char_p(bytes(value, encoding))
	result = cDecrypt(value_bytes)
	return result.decode(encoding)

print(bin_path)