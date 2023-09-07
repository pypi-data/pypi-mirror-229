from starlette.responses import HTMLResponse

from api.app import app
from api.docs.redoc import get_redoc_html
from system import relative

doc_string = str(get_redoc_html(
		openapi_url=f'http://localhost:3000{str(app.openapi_url)}', title=str(app.title) + " - ReDoc"
	).body.decode('utf-8'))

#with open('index.html', 'w') as html:
#	html.write(doc_string)
#

