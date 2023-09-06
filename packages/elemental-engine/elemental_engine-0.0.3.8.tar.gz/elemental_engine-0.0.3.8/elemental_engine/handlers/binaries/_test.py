from elemental_engine.handlers.binaries import encrypt, decrypt, buffer_size

test_string = ''.join(
	['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
	 'x', 'z']*256)

test_string = test_string[0:buffer_size-2]
print(len(test_string))
test_string = 'Mm12052015@'

for i in range(150):
	test_var = encrypt(test_string)
	result = decrypt(test_var)
	print(result)
