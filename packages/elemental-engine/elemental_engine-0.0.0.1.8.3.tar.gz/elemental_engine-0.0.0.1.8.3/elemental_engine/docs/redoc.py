import os.path
from elemental_engine.common import relative
from fastapi.responses import HTMLResponse


def get_redoc_html(
		*,
		openapi_url: str,
		title: str,
		redoc_favicon_url: str = "/static/docs/android-chrome-512x512.png",
		with_google_fonts: bool = True,
) -> HTMLResponse:
	html = f"""<!DOCTYPE html><html><head><title>{title}</title><!-- needed for adaptive design --><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1">"""
	if with_google_fonts:
		html += """<link href="https://fonts.googleapis.com/css?family=Inter:300,400,700|Inter:300,400,700" rel="stylesheet">"""
		html += f"""<link rel="shortcut icon" href="{redoc_favicon_url}">
			</head> 
			<body>
			<div id="redoc-container">

			</div>
			<script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.55/bundles/redoc.standalone.js"></script>
			<script src="/static/docs/try.js"></script>
			<script>

			const fingerprint = function () {{var e,n=window||global,r=(e=(navigator.mimeTypes.length+navigator.userAgent.length).toString(36)+function(t){{var e=[];for(var r in n)e.push(r);return e.length.toString(36)}}(),(new Array(5).join("0")+e).slice(-4)),i=n.screen.width.toString(36),o=n.screen.height.toString(36),g=n.screen.availWidth.toString(36),a=n.screen.availHeight.toString(36),h=n.screen.colorDepth.toString(36),l=n.screen.pixelDepth.toString(36);return btoa(r+i+o+g+a+h+l)}};

			const defaultParameter = function (name, value) {{
			  const elements = document.querySelectorAll(`[placeholder=${{name}}]`);
  			for (let i = 0; i < elements.length; i++) {{
    			const element = elements[i];
    				if (element.type === 'text') {{
      					element.setAttribute('value', value);
      					element.value = value;
    				}}
				}};
			}}

			function setCookie(name, value, days) {{const expires = new Date(); expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000)); document.cookie = name + '=' + value + ';expires=' + expires.toUTCString();}};

			const currentFingerprint = fingerprint();

			setCookie('fingerprint', currentFingerprint, 30);

			/*defaultParameter('fingerprint_cookie', currentFingerprint)*/

			initTry({{
			openApi: `{openapi_url}`,
			redocOptions: {{scrollYOffset: 0, disableSidebar: false}},
			}})

			</script>
			<script src="/static/docs/adapt.js"></script>
			<link rel="stylesheet" href="/static/docs/style/try.css">
			<link rel="stylesheet" href="/static/docs/style/app.css">
			</body></html>
			"""

	return HTMLResponse(html)
