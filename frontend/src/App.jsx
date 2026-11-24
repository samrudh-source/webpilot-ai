import { useEffect, useState } from 'react'
import { Activity, CheckCircle2, Clock3, FileCheck2, Globe2, Pause, Play, ShieldCheck, Square, XCircle } from 'lucide-react'
import './App.css'

const api = async (path, options) => {
  const response = await fetch(path, options)
  if (!response.ok) throw new Error((await response.json()).detail || 'Request failed')
  return response.json()
}

function App() {
  const [workflows, setWorkflows] = useState([])
  const [logs, setLogs] = useState([])
  const [selected, setSelected] = useState(null)
  const [url, setUrl] = useState('http://localhost:8000/sandbox/scholarship')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [proposals, setProposals] = useState([])
  const [applicant] = useState({
    full_name: 'Alex Morgan', email: 'alex@example.com', gpa: '3.7',
    statement: 'I am committed to advancing my studies and supporting my community.'
  })

  const refresh = async () => {
    const [items, audit] = await Promise.all([api('/api/workflows'), api('/api/audit')])
    setWorkflows(items); setLogs(audit)
  }

  useEffect(() => { refresh().catch(e => setError(e.message)) }, [])

  const analyze = async (event) => {
    event.preventDefault(); setBusy(true); setError('')
    try {
      const item = await api('/api/discovery/analyze', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({url, applicant})
      })
      setSelected(item); await refresh()
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  const prepare = async () => {
    if (!selected) return
    setBusy(true)
    try {
      const result = await api(`/api/workflows/${selected.id}/prepare`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({applicant})
      })
      setProposals(result.proposals); await refresh()
    } catch (e) { setError(e.message) } finally { setBusy(false) }
  }

  const act = async (operation) => {
    if (!selected) return
    await api(`/api/workflows/${selected.id}/${operation}`, {method: 'POST'}); await refresh()
  }

  const approve = async () => {
    await api(`/api/workflows/${selected.id}/approve`, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({approved: true})
    })
    await refresh()
  }

  const result = selected?.result
  return (
    <div className="shell">
      <aside>
        <div className="brand"><ShieldCheck size={22}/><strong>WebPilot</strong><span>AI</span></div>
        <nav><button className="active"><Activity size={18}/>Overview</button><button><Globe2 size={18}/>Discover</button><button><FileCheck2 size={18}/>Applications</button><button><ShieldCheck size={18}/>Audit trail</button></nav>
        <div className="policy"><ShieldCheck size={17}/><div><b>Human control</b><small>All submissions require approval</small></div></div>
      </aside>
      <main>
        <header><div><p>OPERATIONS / OVERVIEW</p><h1>Command Center</h1></div><div className="system"><span/>Systems operational</div></header>
        {error && <div className="error"><XCircle size={16}/>{error}</div>}
        <section className="metrics">
          <article><span><Activity size={18}/></span><div><small>Active workflows</small><strong>{workflows.filter(w => !['cancelled','completed'].includes(w.status)).length}</strong></div></article>
          <article><span className="cyan"><CheckCircle2 size={18}/></span><div><small>Evidence sources</small><strong>{result?.eligibility?.length || 0}</strong></div></article>
          <article><span className="amber"><Clock3 size={18}/></span><div><small>Awaiting approval</small><strong>{proposals.length ? 1 : 0}</strong></div></article>
        </section>
        <div className="grid">
          <section className="card discover">
            <div className="card-title"><div><small>NEW TASK</small><h2>Website discovery</h2></div><Globe2 size={20}/></div>
            <form onSubmit={analyze}><label>Target URL</label><div className="url-row"><input value={url} onChange={e => setUrl(e.target.value)} aria-label="Target URL"/><button disabled={busy}>{busy ? 'Analyzing…' : 'Analyze'}</button></div></form>
            <div className="sandbox"><ShieldCheck size={16}/><div><b>Sandbox mode</b><small>Official portal integrations are not configured.</small></div></div>
          </section>
          <section className="card viewport"><div className="card-title"><div><small>BROWSER ACTIVITY</small><h2>Portal viewport</h2></div><span className="live">SIMULATED</span></div><iframe title="Sandbox scholarship portal" src="/sandbox/scholarship"/></section>
          <section className="card evidence"><div className="card-title"><div><small>SOURCE EVIDENCE</small><h2>Eligibility rules</h2></div></div>
            {result?.eligibility?.length ? result.eligibility.map((item, i) => <div className="rule" key={i}><CheckCircle2 size={16}/><div><p>{item.rule}</p><a href={item.source} target="_blank" rel="noreferrer">{item.source}</a></div></div>) : <p className="empty">Analyze the sandbox portal to extract evidence.</p>}
          </section>
          <section className="card checklist"><div className="card-title"><div><small>REQUIRED ITEMS</small><h2>Document checklist</h2></div><FileCheck2 size={20}/></div>
            {(result?.documents || []).map((item, i) => <label className="check" key={i}><input type="checkbox"/><span>{item}</span></label>)}
            {result?.documents && <button className="secondary" onClick={prepare} disabled={!selected || busy}>Prepare permitted fields</button>}
          </section>
          <section className="card approval"><div className="card-title"><div><small>HUMAN APPROVAL</small><h2>Proposed actions</h2></div><ShieldCheck size={20}/></div>
            {proposals.length ? <>{proposals.map((p,i)=><div className="proposal" key={i}><b>{p.action}</b><span>{p.field}</span><code>{p.value}</code></div>)}<div className="approval-actions"><button className="approve" onClick={approve}><CheckCircle2 size={16}/>Approve preparation</button><button className="reject" onClick={()=>setProposals([])}>Reject</button></div></> : <p className="empty">No actions awaiting approval. Submission remains disabled.</p>}
          </section>
          <section className="card audit"><div className="card-title"><div><small>EXECUTION TRAIL</small><h2>Audit log</h2></div></div>
            {logs.slice(0,5).map(log => <div className="log" key={log.id}><span/><div><b>{log.action}</b><small>{log.timestamp?.slice(11,19)} UTC · {log.status}</small></div></div>)}
          </section>
        </div>
        {selected && <div className="workflow-bar"><b>{selected.title}</b><span className={`status ${selected.status}`}>{selected.status}</span><button onClick={()=>act('pause')}><Pause size={15}/>Pause</button><button onClick={()=>act('resume')}><Play size={15}/>Resume</button><button onClick={()=>act('cancel')}><Square size={15}/>Cancel</button></div>}
      </main>
    </div>
  )
}

export default App
