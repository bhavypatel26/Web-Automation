import {useEffect, useState, type FormEvent} from 'react';
import {jsonRequest, request} from '../api/client';
import type {Workflow, Run} from '../types';

type ChatTurn = {command: string; skill: string; run: Run};

export function RunWorkflow({workflows}: {workflows: Workflow[]}) {
  const [skillId, setSkillId] = useState('');
  const [command, setCommand] = useState('');
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const selected = workflows.find(workflow => workflow.id === skillId);
  const latest = turns.at(-1)?.run;
  const active = latest && ['queued', 'running'].includes(latest.status);

  useEffect(() => {
    if (!active || !latest) return;
    const timer = setInterval(() => request<Run>('/workflow-runs/' + latest.id).then(run => {
      setTurns(current => current.map(turn => turn.run.id === run.id ? {...turn, run} : turn));
    }).catch(error => setError(error.message)), 1000);
    return () => clearInterval(timer);
  }, [latest?.id, active]);

  async function send(event: FormEvent) {
    event.preventDefault();
    if (!selected || !command.trim()) return;
    setBusy(true); setError('');
    try {
      const run = await jsonRequest<Run>('/workflow-runs', {workflow_id: selected.id, message: command});
      setTurns(current => [...current, {command, skill: selected.name, run}]);
      setCommand('');
    } catch (error) {setError((error as Error).message);}
    finally {setBusy(false);}
  }

  return <section className={'agent-chat ' + (turns.length ? 'has-messages' : 'empty-chat')}>
    {!turns.length && <h1>What would you like to get done?</h1>}
    {turns.length > 0 && <div className="chat-history" aria-live="polite">
      {turns.map(turn => <div className="chat-turn" key={turn.run.id}>
        <div className="chat-message user-message"><p>{turn.command}</p></div>
        <div className="chat-message assistant-message"><span className="message-meta">Workflow · {turn.run.status.replaceAll('_', ' ')}</span>
          <p>{turn.run.summary || turn.run.stage}</p>
          {turn.run.files.map(file => <p key={file}><a href={'/api/files/downloads/' + file}>↓ {file.split('/').pop()}</a></p>)}
        </div>
      </div>)}
    </div>}
    <form className="chat-composer" onSubmit={send}>
      <textarea aria-label="Your command" rows={1} value={command} onChange={event => setCommand(event.target.value)} disabled={busy || !!active} placeholder="Ask your workflow agent" onKeyDown={event => {if (event.key === 'Enter' && !event.shiftKey) {event.preventDefault(); event.currentTarget.form?.requestSubmit();}}} />
      <div className="composer-toolbar"><select aria-label="Select skill" value={skillId} disabled={busy || !!active} onChange={event => setSkillId(event.target.value)}>
        <option value="">Select skill</option>{workflows.map(workflow => <option key={workflow.id} value={workflow.id}>{workflow.name}</option>)}
      </select>
      {active ? <button type="button" className="send-button" aria-label="Cancel execution" onClick={() => jsonRequest<Run>('/workflow-runs/' + latest.id + '/cancel', {}).catch(error => setError(error.message))}>■</button>
        : <button className="send-button" aria-label="Send command" disabled={!selected || !command.trim() || busy}>{busy ? '…' : '↑'}</button>}
      </div>
    </form>
    {error && <p className="error" role="alert">{error}</p>}
  </section>;
}
