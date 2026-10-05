import {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {request} from './api/client';
import {CreateWorkflow} from './components/CreateWorkflow';
import {ReviewWorkflow} from './components/ReviewWorkflow';
import {RunWorkflow} from './components/RunWorkflow';
import type {Workflow} from './types';
import './style.css';

function App() {
  const [tab, setTab] = useState('create');
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selected, setSelected] = useState<Workflow | null>(null);
  const [error, setError] = useState('');
  function reload() {
    request<Workflow[]>('/workflows').then(setWorkflows).catch(error => setError(error.message));
  }
  useEffect(reload, []);
  function saved(workflow: Workflow) {setSelected(workflow); reload();}
  return <main>
    <header className="app-header"><div className="brand">Workflow</div>
    <nav aria-label="Mode">{[['create','Chat'],['run','Work']].map(([id,label]) => <button aria-pressed={tab === id} className={tab === id ? 'selected' : ''} key={id} onClick={() => setTab(id)}>{label}</button>)}</nav></header>
    {error && <p role="alert" className="error">{error}</p>}
    {tab === 'create' && <>{!selected ? <CreateWorkflow onCreated={saved} /> : <>
      <button className="secondary" onClick={() => setSelected(null)}>Create another workflow</button>
      <ReviewWorkflow key={selected.id + '-' + selected.version} workflow={selected} onSaved={workflow => {saved(workflow); setTab('run');}} />
    </>}</>}
    {tab === 'run' && <RunWorkflow workflows={workflows} />}
    <footer>Your workflows, on your machine.</footer>
  </main>;
}
createRoot(document.getElementById('root')!).render(<App />);
