import json

from elemental_engine.common import get_system_info

test_string = 'abcdefghijklmnopqrstuvwxyz'
print(f'Test Result: {json.dumps(get_system_info(test_string, True), indent=2)}')