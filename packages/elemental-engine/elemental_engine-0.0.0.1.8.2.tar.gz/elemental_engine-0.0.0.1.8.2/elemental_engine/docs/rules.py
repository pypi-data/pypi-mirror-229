product_id_length = 24


password_rule_length = 8
password_rule = """
password must have at least eight characters.
"""

username_rule_length = 4
username_rule = """
username must have at least 4 characters.
"""

def already_taken(title):
	return f"""{title} is in use."""

def invalid(title):
	return f"""{title} informed is invalid."""