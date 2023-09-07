from elemental_engine.middleware.cors import CORSMiddleware
from elemental_engine.middleware.auth import auth_middleware

def enable_cors(app):
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

def enable_auth(app):
	app.middleware('http')(auth_middleware)
