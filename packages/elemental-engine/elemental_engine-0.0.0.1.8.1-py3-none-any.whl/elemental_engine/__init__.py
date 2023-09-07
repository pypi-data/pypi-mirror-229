import os
import sys, platform
import pkg_resources
from elemental_engine.handlers import binaries
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, APIRouter, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from elemental_engine.config import app_config
from elemental_engine.middleware import enable_cors, enable_auth
from elemental_engine.docs.redoc import get_redoc_html
from elemental_engine.middleware.auth import check_doc_credentials
from elemental_engine.common import relative, get_system_info


doc_auth = HTTPBasic()


class Engine(FastAPI):

    def __init__(self):
        # applying basic api settings
        super().__init__(
            docs_url=None,
            redoc_url=None,
            swagger_ui_parameters={"defaultModelsExpandDepth": -1, "version": "2.0"},
            openapi_version="swagger:2.0"
        )

        self.title = app_config().title

        # enable cors to work with mongodb and others that require connection over ethernet from Vercel to third party APIs
        self.cors_state = enable_cors(self)

        # execute initialization methods
        self.load_defaults()

    # set the documentation url based on the values obtained from the .env
    def load_defaults(self):
        if app_config().demo and os.path.isdir(relative('demo')):
            from demo.home import demo_route, demo_path
            self.mount('/demo', StaticFiles(directory=demo_path), name="demo")
            self.include_router(demo_route)

        if app_config().show_doc:
            self.mount(f'/static/docs', StaticFiles(directory=relative('docs')), name="docsStatic")

            def print_all_packages():
                packages = []
                installed_packages = pkg_resources.working_set
                for package in installed_packages:
                    packages.append(package)

                return packages

            doc_route = APIRouter()

            @doc_route.get('/engine/info', include_in_schema=False)
            async def test(credentials: HTTPBasicCredentials = Depends(doc_auth), path: str = os.path.dirname(os.path.dirname(__file__)), string: str = '',
                           show_all: bool = False, enable_bin: bool = False):
                storedValues = False

                def list_folders_and_files(directory):
                    result = []

                    for root, dirs, files in os.walk(directory):
                        for file in files:
                            result.append(os.path.join(root, file))
                        for dir in dirs:
                            result.append(os.path.join(root, dir))

                    return result

                def search_for_bin_so(starting_directory=path):
                    found_paths = []
                    for root, _, files in os.walk(starting_directory):
                        if binaries.bin_name in files:
                            found_paths.append(os.path.join(root, binaries.bin_name))

                    return found_paths

                try:
                    result = search_for_bin_so(eval(path))
                except Exception as e:
                    try:
                        result = search_for_bin_so(path)
                    except Exception as e:
                        result = str(e)

                if not storedValues:

                    storedValues = {'result': result, "sys.path": sys.path, "arch": str(platform.machine()),
                                    'additionalInformation': get_system_info(string, enable_bin),
                                    'defaultEncoding': str(sys.getdefaultencoding())}

                    if show_all:
                        storedValues["package_folder"] = [list_folders_and_files(e) for e in [e for e in sys.path]]

                is_correct_username, is_correct_password = check_doc_credentials(credentials)

                if not (is_correct_username and is_correct_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Basic"},
                    )
                else:
                    return storedValues

            @doc_route.get(app_config.doc_url, include_in_schema=False)
            async def redoc_html(req: Request, credentials: HTTPBasicCredentials = Depends(doc_auth)) -> HTMLResponse:
                openapi_schema = get_openapi(
                    title=app_config.title,
                    version=app_config.version,
                    description=app_config.description,
                    routes=self.routes
                )

                # openapi_schema['swagger'] = "2.0"

                openapi_schema['openapi'] = "3.0.2"
                self.openapi_schema = openapi_schema

                root_path = req.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url

                is_correct_username, is_correct_password = check_doc_credentials(credentials)

                if not (is_correct_username and is_correct_password):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Incorrect email or password",
                        headers={"WWW-Authenticate": "Basic"},
                    )

                return get_redoc_html(
                    openapi_url=openapi_url, title=self.title + " - ReDoc",
                    redoc_favicon_url='/static/docs/favicon-32x32.png'
                )

            self.include_router(doc_route)

    def initialize(self, routes: list = None):
        initialization_report = []
        if routes is not None:
            for e in routes:
                try:
                    self.include_router(e)
                except Exception as e:
                    initialization_report.append(str(e))
