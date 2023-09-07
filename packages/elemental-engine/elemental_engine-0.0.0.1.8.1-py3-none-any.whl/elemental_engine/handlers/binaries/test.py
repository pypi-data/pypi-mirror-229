from elemental_engine.handlers.binaries import encrypt, decrypt, buffer_size

class result:
    initial_string = ''.join(['a', 'b', 'c', 'd', 'e', 'f', 'g', ' '] * 256)
    test_length = 100

    def __init__(self, test_string=initial_string):
        print(f'Test string: %s' % test_string)
        self.test_string = test_string
        self.encrypted_string = encrypt(self.test_string)

        self.decrypted_string = decrypt(self.encrypted_string)

        test_result = []

        for i in range(self.test_length):
            test_result.append({self.decrypted_string == self.test_string})

        self.test_total_length = int(self.test_length * len(self.test_string))
        self.result = all(test_result)
