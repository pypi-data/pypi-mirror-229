import json

from elemental_engine.common import get_system_info

test_string = 'abc'
print(f'Test Result: {json.dumps(get_system_info(test_string, enable_test_bin=True), indent=2)}')