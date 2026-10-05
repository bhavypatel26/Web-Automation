from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class WorkflowInput(BaseModel):
    name: str
    label: str
    kind: Literal['text', 'file'] = 'text'
    required: bool = True
    default: str | None = None


class WorkflowStep(BaseModel):
    instruction: str
    expected_result: str
    submits_form: bool = False


class Workflow(BaseModel):
    id: str
    version: int = 1
    name: str
    description: str
    portal_url: HttpUrl
    allowed_hosts: list[str] = Field(default_factory=list)
    inputs: list[WorkflowInput] = Field(default_factory=list)
    steps: list[WorkflowStep] = Field(default_factory=list)
    completion: str = ''
    skill: str = ''
    status: Literal['draft', 'published'] = 'draft'
    submissions_authorized: bool = False
    recording: str | None = None


class WorkflowRun(BaseModel):
    id: str
    workflow_id: str
    workflow_version: int
    message: str
    status: str = 'queued'
    stage: str = 'Waiting for browser worker'
    summary: str = ''
    files: list[str] = Field(default_factory=list)


class StartRun(BaseModel):
    workflow_id: str
    message: str = ''

