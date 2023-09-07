from sys import stderr

from elemental_engine.docs.descriptions.endpoints import example  # Use this to import your descriptions


def loadDescription(endpoint, method):
	try:
		return getattr(eval(endpoint), method)()
	except Exception as e:
		stderr.write(str(e) + '\n')
		return ''
