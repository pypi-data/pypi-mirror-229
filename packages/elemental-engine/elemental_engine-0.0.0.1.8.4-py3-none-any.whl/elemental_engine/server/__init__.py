import uvicorn
from elemental_engine.config import app_config

def run(app: any, reload: bool = False):
    try:
        uvicorn.run(app, host=app_config().host, port=app_config().port, reload=app_config().debug | reload)
    except (ValueError, KeyError, Exception) as e:
        raise Exception(e)
