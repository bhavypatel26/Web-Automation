import asyncio
import uuid
from models.workflow import WorkflowRun
from tools.browser_use_executor import BrowserUseExecutor


class WorkflowRunner:
    def __init__(self, storage):
        self.storage = storage
        self.queue = asyncio.Queue()
        self.runs = {run.id: run for run in storage.runs()}
        self.browsers = {}
        self.active = None
        self.worker = None
        for run in self.runs.values():
            if run.status in ['queued','running','authentication_required']:
                run.status = 'interrupted'
                run.stage = 'Backend restarted; inspect the portal before creating a new run'
                storage.save_run(run)

    def start(self, request):
        workflow = self.storage.workflow(request.workflow_id)
        if any(step.submits_form for step in workflow.steps) and not workflow.submissions_authorized:
            raise ValueError('Authorize the listed submissions when saving this workflow')
        run = WorkflowRun(id=str(uuid.uuid4()), workflow_id=workflow.id, workflow_version=workflow.version,
                          message=request.message)
        self.runs[run.id] = run
        self.storage.save_run(run)
        self.queue.put_nowait((run, workflow.model_copy(deep=True)))
        if self.worker is None or self.worker.done():
            self.worker = asyncio.create_task(self.work())
        return run

    def update(self, run, status, stage):
        run.status = status
        run.stage = stage
        self.storage.save_run(run)

    async def work(self):
        while not self.queue.empty():
            run, workflow = await self.queue.get()
            if run.status != 'cancelled':
                self.active = asyncio.create_task(self.execute(run, workflow))
                await self.active
            self.queue.task_done()

    async def execute(self, run, workflow):
        executor = BrowserUseExecutor(self.storage, run, workflow, self)
        try:
            self.update(run, 'running', 'Opening Browser Use')
            async with asyncio.timeout(600):
                result = await executor.execute()
            run.summary = result.summary
            self.update(run, 'success' if result.success else 'needs_review', result.summary)
        except asyncio.CancelledError:
            self.update(run, 'cancelled', 'Cancelled; inspect the portal before repeating a submission')
        except TimeoutError:
            self.update(run, 'timeout', 'Run exceeded ten minutes')
        except Exception as exc:
            self.update(run, 'failed', f'Browser Use execution failed ({type(exc).__name__})')

    def cancel(self, identifier):
        run = self.runs[identifier]
        if run.status == 'queued':
            self.update(run, 'cancelled', 'Cancelled before starting')
        elif run.status == 'running' and self.active:
            self.active.cancel()
        return run

    async def close(self):
        if self.active and not self.active.done():
            self.active.cancel()
        if self.worker:
            await self.worker

        for browser in self.browsers.values():
            await browser.kill()
