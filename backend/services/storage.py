import json
import os
import yaml
from pathlib import Path
from config import ROOT
from models.workflow import Workflow, WorkflowRun


class Storage:
    def __init__(self, root: Path = ROOT / 'local-data'):
        self.root = root
        for folder in ['workflows', 'recordings', 'runs', 'uploads', 'downloads']:
            (root / folder).mkdir(parents=True, exist_ok=True)

    def write(self, path, data):
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
        os.replace(temporary, path)

    def workflows(self):
        return [Workflow.model_validate_json(p.read_text(encoding='utf-8')) for p in (self.root / 'workflows').glob('*/current.json')]

    def workflow(self, identifier):
        return next(w for w in self.workflows() if w.id == identifier)

    def save_workflow(self, workflow):
        folder = self.root / 'workflows' / workflow.id
        folder.mkdir(exist_ok=True)
        self.write(folder / 'current.json', workflow.model_dump(mode='json'))
        self.write(folder / f'version-{workflow.version}.json', workflow.model_dump(mode='json'))
        (folder / 'workflow.yaml').write_text(yaml.safe_dump(workflow.model_dump(mode='json'), sort_keys=False), encoding='utf-8')
        (folder / 'SKILL.md').write_text(workflow.skill, encoding='utf-8')

    def save_run(self, run):
        self.write(self.root / 'runs' / f'{run.id}.json', run.model_dump())

    def runs(self):
        return [WorkflowRun.model_validate_json(p.read_text(encoding='utf-8')) for p in (self.root / 'runs').glob('*.json')]

    def file(self, category, filename):
        base = (self.root / category).resolve()
        path = (base / filename).resolve()
        if not path.is_relative_to(base) or not path.is_file():
            raise ValueError('File not found')
        return path
