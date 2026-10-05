import {useState, type FormEvent} from 'react';
import {request, upload} from '../api/client';
import type {Workflow} from '../types';

export function CreateWorkflow({onCreated}: {onCreated: (workflow: Workflow) => void}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const body = new FormData(event.currentTarget);
    const video = body.get('video') as File;
    setBusy(true); setError('');
    try {
      body.delete('video');
      body.set('recording', await upload(video, 'recordings'));
      body.set('clean_recording', 'true');
      onCreated(await request<Workflow>('/workflows/analyze', {method: 'POST', body}));
    } catch (error) {setError((error as Error).message);}
    finally {setBusy(false);}
  }
  return <div className="create-view">
    <h1>What would you like to automate?</h1>
    <form className="creation-composer" onSubmit={submit}>
      <textarea aria-label="Workflow context" name="description" required placeholder="Describe your workflow and the outcome you want..." />
      <div className="creation-details">
        <input aria-label="Workflow name" name="name" required placeholder="Workflow name" />
        <input aria-label="Website URL" name="portal_url" type="url" required placeholder="Website URL" />
      </div>
      <div className="composer-toolbar"><label className="attachment">+ Add recording<input name="video" type="file" accept="video/mp4,video/webm,video/quicktime" required /></label>
      <button className="send-button" aria-label="Create workflow" disabled={busy}>{busy ? '…' : '↑'}</button></div>
      <label className="check"><input type="checkbox" required /> My recording contains no credentials or sensitive screens. Frames are sent to Azure.</label>
    </form>
    {busy && <p className="hint" role="status">Reading your recording and creating the workflow...</p>}
    {error && <p role="alert" className="error">{error}</p>}
  </div>;
}
