from starlette.requests import Request
from starlette.templating import Jinja2Templates

# new テンプレート関連の設定 (jinja2)
templates = Jinja2Templates(directory="templates")
jinja_env = templates.env  # Jinja2.Environment : filterやglobalの設定用
 
 
def index(request: Request):
    return templates.TemplateResponse('index.html',
                                      {'request': request})