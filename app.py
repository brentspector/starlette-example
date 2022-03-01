from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from filestorage import store
from filestorage.filters import RandomizeFilename
from filestorage.handlers import AsyncLocalFileHandler
import uvicorn


templates = Jinja2Templates(directory='templates')

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='statics'), name='static')


@app.route('/')
async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


@app.route('/error')
async def error(request):
    """
    An example error. Switch the `debug` setting to see either tracebacks or 500 pages.
    """
    raise RuntimeError("Oh no")


@app.exception_handler(404)
async def not_found(request, exc):
    """
    Return an HTTP 404 page.
    """
    template = "404.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    """
    Return an HTTP 500 page.
    """
    template = "500.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context, status_code=500)

@app.route('/upload', methods=['GET', 'POST'])
async def uploader(request):
    template = "file_upload.html"
    context = {"request": request}
    if request.method == 'GET':
        return templates.TemplateResponse(template, context)
    form = await request.form()
    context['uploaded_filename'] = await store.async_save_field(form['file'])
    return templates.TemplateResponse(template, context)


if __name__ == "__main__":
    store.handler = AsyncLocalFileHandler(
        base_path='uploads', filters=[RandomizeFilename()], auto_make_dir=True,
    )
    store.finalize_config()
    uvicorn.run(app, host='0.0.0.0', port=8000)
