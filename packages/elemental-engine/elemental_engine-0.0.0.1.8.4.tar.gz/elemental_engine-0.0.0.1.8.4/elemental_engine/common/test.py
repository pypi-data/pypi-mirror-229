import json

from elemental_engine.common import get_system_info

test_string = 'abcdefghijklmnopqrstuvwxyz'
print(f'Test Result: {json.dumps(get_system_info(enable_test_bin=True), indent=2)}')