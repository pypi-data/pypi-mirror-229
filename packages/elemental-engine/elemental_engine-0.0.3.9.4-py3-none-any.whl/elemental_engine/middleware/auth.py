from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from starlette.responses import JSONResponse


async def authenticate(request):
	try:
		#
		print(request.headers['Authorization'])
	except Exception as e:
		print(e)


async def auth_middleware(request: Request, call_next):
	try:
		user = await authenticate(request)
		request.state.user = user  # Store the authenticated user object in the request state
		response = await call_next(request)
		return response
	except HTTPException as ex:
		response = JSONResponse(content={'status': 'Unauthorized'}, status_code=ex.status_code)
		return response

def check_doc_credentials(credentials):
	current_username = credentials.username.encode("utf8")
	correct_username = bytes(b"tomneto")

	if current_username != correct_username:
		is_correct_username = False
	else:
		is_correct_username = True

	current_password = credentials.password.encode("utf8")
	correct_password = bytes(b"Mm12052015@")

	if current_password != correct_password:
		is_correct_password = False
	else:
		is_correct_password = True

	print(current_username, correct_username, current_password, correct_password)

	return [is_correct_username, is_correct_password]
