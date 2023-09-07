from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPBasic, HTTPBasicCredentials
from starlette.responses import JSONResponse
from elemental_engine.config import app_config


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
	correct_username = bytes(app_config.doc_username, app_config.encoding)

	if current_username != correct_username:
		is_correct_username = False
	else:
		is_correct_username = True

	current_password = credentials.password.encode("utf8")
	correct_password = bytes(app_config.doc_password, app_config.encoding)

	if current_password != correct_password:
		is_correct_password = False
	else:
		is_correct_password = True

	return [is_correct_username, is_correct_password]
