import {useState} from 'react';
import {jsonRequest} from '../api/client';
import type {Workflow} from '../types';

export function ReviewWorkflow({workflow, onSaved}: {workflow: Workflow; onSaved: (workflow: Workflow) => void}) {
  const [draft, setDraft] = useState(workflow);
  const [error, setError] = useState('');
  const [yaml, setYaml] = useState('');
  async function save() {
    try {onSaved(await jsonRequest<Workflow>('/workflows/' + draft.id, draft, 'PUT')); setError('');}
    catch (error) {setError((error as Error).message);}
  }
  return <section>
    <div className="eyebrow">{draft.status} · VERSION {draft.version}</div><h2>{draft.name}</h2>
    <p>Review the generated skill and workflow steps, then save the workflow to make it available for execution.</p>
    <label>Workflow name<input value={draft.name} onChange={e => setDraft({...draft, name: e.target.value})} /></label>
    <label>Expected outcome<textarea value={draft.completion} onChange={e => setDraft({...draft, completion: e.target.value})} /></label>
    <details><summary>Website settings</summary><label>Allowed hosts<input value={draft.allowed_hosts.join(', ')} onChange={e => setDraft({...draft, allowed_hosts: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})} /></label></details>
    {draft.steps.map((step, index) => <div className="step" key={index}>
      <label>Step {index + 1}<textarea value={step.instruction} onChange={e => setDraft({...draft, steps: draft.steps.map((s, i) => i === index ? {...s, instruction: e.target.value} : s)})} /></label>
      <label>Expected result<input value={step.expected_result} onChange={e => setDraft({...draft, steps: draft.steps.map((s, i) => i === index ? {...s, expected_result: e.target.value} : s)})} /></label>
      <label className="check"><input type="checkbox" checked={step.submits_form} onChange={e => setDraft({...draft, steps: draft.steps.map((s, i) => i === index ? {...s, submits_form: e.target.checked} : s)})} /> This step submits a form</label>
    </div>)}
    <details><summary>Changing inputs</summary>
    {draft.inputs.map((field, index) => <div className="step" key={index}>
      <label>Input label<input value={field.label} onChange={e => setDraft({...draft, inputs: draft.inputs.map((item, i) => i === index ? {...item, label: e.target.value} : item)})} /></label>
      <label>Default value<input value={field.default ?? ''} disabled={field.kind === 'file'} onChange={e => setDraft({...draft, inputs: draft.inputs.map((item, i) => i === index ? {...item, default: e.target.value || null} : item)})} /></label>
      <label className="check"><input type="checkbox" checked={field.required} onChange={e => setDraft({...draft, inputs: draft.inputs.map((item, i) => i === index ? {...item, required: e.target.checked} : item)})} /> Required for execution</label>
    </div>)}
    {!draft.inputs.length && <p>This workflow has no changing inputs.</p>}
    </details>
    <details><summary>View generated files</summary>
    <label>SKILL.md<textarea value={draft.skill} onChange={e => setDraft({...draft, skill: e.target.value})} /></label>
    <button className="secondary" onClick={async () => {try {const response = await fetch('/api/workflows/' + draft.id + '/export'); if (!response.ok) throw new Error('Could not load YAML'); setYaml(await response.text());} catch (error) {setError((error as Error).message);}}}>View saved YAML</button>
    {yaml && <pre>{yaml}</pre>}
    <a href={'/api/workflows/' + draft.id + '/export'}>Download saved YAML</a>
    <p>Generated files reflect the saved workflow. Save your edits to update them.</p></details>
    {draft.steps.some(step => step.submits_form) && <label className="check"><input type="checkbox" checked={draft.submissions_authorized} onChange={e => setDraft({...draft, submissions_authorized: e.target.checked})} /> Authorize the listed submissions, including the test run.</label>}
    <button onClick={save}>Save workflow</button>

    {error && <p className="error" role="alert">{error}</p>}
  </section>;
}
