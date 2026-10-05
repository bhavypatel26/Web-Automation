from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from config import Settings
from services.azure_client import AzureClient
from services.storage import Storage
from services.authoring import Authoring
from services.workflow_runner import WorkflowRunner
from routers.workflows import create_router

azure = AzureClient(Settings())
storage = Storage()
workflow_runner = WorkflowRunner(storage)
local_origins = ['http://127.0.0.1:5173', 'http://localhost:5173']


@asynccontextmanager
async def lifespan(app):
    yield
    await workflow_runner.close()
    await azure.close()


app = FastAPI(lifespan=lifespan)
app.include_router(create_router(storage, Authoring(storage, azure), workflow_runner))
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1', 'testserver'])
app.add_middleware(CORSMiddleware, allow_origins=local_origins, allow_methods=['GET', 'POST', 'PUT'], allow_headers=['Content-Type'])


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo submitted credential values in validation responses.
    return JSONResponse({'detail': 'Invalid request fields'}, status_code=422)


@app.middleware('http')
async def origin_guard(request: Request, call_next):
    if request.headers.get('origin') not in [None, *local_origins]:
        return JSONResponse({'detail': 'Origin not allowed'}, status_code=403)
    return await call_next(request)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000, access_log=False)
