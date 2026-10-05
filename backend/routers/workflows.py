import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, Response
from models.workflow import Workflow, StartRun
from services.azure_client import ConfigurationFailure, ModelFailure


def create_router(storage, authoring, runner):
    router = APIRouter(prefix='/api')

    def find_workflow(identifier):
        try:
            return storage.workflow(identifier)
        except StopIteration:
            raise HTTPException(404, 'Workflow not found') from None

    def find_run(identifier):
        if identifier not in runner.runs:
            raise HTTPException(404, 'Run not found')
        return runner.runs[identifier]

    @router.get('/workflows')
    async def list_workflows():
        return storage.workflows()

    @router.post('/uploads/{category}')
    async def upload(category: str, file: UploadFile = File(...)):
        if category not in ['recordings', 'uploads']:
            raise HTTPException(400, 'Unsupported upload category')
        from pathlib import Path
        suffix = Path(file.filename or '').suffix
        if category == 'recordings' and suffix.lower() not in ['.mp4','.webm','.mov']:
            raise HTTPException(400, 'Upload MP4, WebM or MOV')
        name = str(uuid.uuid4()) + suffix
        path = storage.root / category / name
        size = 0
        try:
            with path.open('wb') as output:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > 500 * 1024 * 1024:
                        raise HTTPException(413, 'Upload limit is 500 MB')
                    output.write(chunk)
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return {'file': name}

    @router.post('/workflows/analyze')
    async def analyze(name: str = Form(...), description: str = Form(...), portal_url: str = Form(...),
                      recording: str = Form(...), clean_recording: bool = Form(...)):
        if not clean_recording:
            raise HTTPException(400, 'Provide a recording without credentials or sensitive screens')
        try:
            return await authoring.create(name, description, portal_url, recording)
        except (ConfigurationFailure, ModelFailure) as exc:
            raise HTTPException(400, f'Analysis failed: {exc}') from None
        except Exception as exc:
            raise HTTPException(400, f'Analysis failed ({type(exc).__name__}). Check recording and Azure settings.') from None

    @router.put('/workflows/{identifier}')
    async def edit(identifier: str, workflow: Workflow):
        old = find_workflow(identifier)
        workflow.id = old.id
        workflow.version = old.version + 1
        workflow.status = 'published'
        storage.save_workflow(workflow)
        return workflow

    @router.get('/workflows/{identifier}/export')
    async def export(identifier: str):
        import yaml
        return Response(yaml.safe_dump(find_workflow(identifier).model_dump(mode='json'), sort_keys=False), media_type='application/yaml')

    @router.post('/workflow-runs', status_code=202)
    async def start(body: StartRun):
        try:
            return runner.start(body)
        except (ValueError, StopIteration) as exc:
            raise HTTPException(400, str(exc) or 'Workflow not found') from None

    @router.get('/workflow-runs')
    async def runs():
        return list(runner.runs.values())

    @router.get('/workflow-runs/{identifier}')
    async def get_run(identifier: str):
        return find_run(identifier)

    @router.post('/workflow-runs/{identifier}/cancel')
    async def cancel(identifier: str):
        find_run(identifier)
        return runner.cancel(identifier)

    @router.get('/files/{category}/{filename:path}')
    async def download(category: str, filename: str):
        if category != 'downloads':
            raise HTTPException(403, 'Only completed downloads are available')
        try:
            return FileResponse(storage.file(category, filename))
        except ValueError:
            raise HTTPException(404, 'File not found')

    return router
