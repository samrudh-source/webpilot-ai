import { NavLink, Route, Routes, useNavigate } from 'react-router-dom'
import { useEffect, useState, type ReactNode } from 'react'
import { Activity, Bot, CheckCircle2, ClipboardCheck, FileCheck2, FileText, Globe2, History as HistoryIcon, LayoutDashboard, LogOut, Play, Settings as SettingsIcon, ShieldCheck, UserRound } from 'lucide-react'
import { api, Workflow } from './services/api'

const nav = [
  ['dashboard','Dashboard',LayoutDashboard],['workspace','AI Agent',Bot],['browser','Browser Viewport',Globe2],
  ['eligibility','Eligibility',ShieldCheck],['profile','Applicant Profile',UserRound],['documents','Documents',FileCheck2],
  ['prepare','Prepare Form',ClipboardCheck],['approval','Approvals',CheckCircle2],['history','Workflow History',HistoryIcon],
  ['audit','Audit Logs',Activity],['settings','Settings',SettingsIcon],
] as const

function Shell({children}:{children:ReactNode}) {
  return <div className="app-shell"><aside><div className="brand"><div className="brand-icon"><Bot size={20}/></div><div><b>WebPilot</b><span>AI</span></div></div>
    <nav>{nav.map(([p,label,Icon])=><NavLink key={p} to={`/${p}`} className={({isActive})=>isActive?'active':''}><Icon size={18}/><span>{label}</span></NavLink>)}</nav>
    <div className="side-footer"><div className="status-dot"/> Browser engine <b>Online</b></div>
  </aside><main>{children}</main></div>
}

function Header({title,subtitle}:{title:string;subtitle:string}){return <header className="page-header"><div><p className="kicker">WEBPILOT AI · INDIA</p><h1>{title}</h1><p>{subtitle}</p></div><button className="avatar">AK</button></header>}

function Landing() {
  const navigate=useNavigate()
  return   <div className="landing"><nav><div className="brand"><div className="brand-icon"><Bot size={20}/></div><b>WebPilot AI India</b></div><button onClick={()=>navigate('/dashboard')} className="outline">Open console</button></nav>
  <div className="hero-wrap"><div className="hero-copy"><div className="announcement">Human-controlled browser intelligence</div><h1>Turn complex web processes into <em>controlled actions.</em></h1><p>WebPilot AI finds the rules, prepares the forms, and keeps every sensitive decision with you.</p><button className="primary" onClick={()=>navigate('/dashboard')}><Play size={17}/> Start a workflow</button></div>
  <div className="hero-visual"><div className="pipeline"><span>Goal</span><i/><span>Plan</span><i/><span>Policy</span><i/><span>Approve</span></div><div className="scan-card"><div><ShieldCheck/><span>Evidence verified</span></div><b>Karnataka scholarship</b><p>6 eligibility requirements detected</p><div className="progress-bar"><i/></div></div></div></div></div>
}

function Dashboard(){
 const [workflows,setWorkflows]=useState<Workflow[]>([])
 const [pendingApprovals,setPendingApprovals]=useState(0)
 const [url,setUrl]=useState('http://127.0.0.1:8000/sandbox')
 const [task,setTask]=useState('Analyze the scholarship requirements and prepare my application.')
 const [creating,setCreating]=useState(false)
 const navigate=useNavigate()
 const load=()=>{
  api<Workflow[]>('/workflows').then(setWorkflows).catch(()=>setWorkflows([]))
  api<any[]>('/approvals').then(rows=>setPendingApprovals(rows.filter(row=>row.status==='pending').length)).catch(()=>setPendingApprovals(0))
 }
 useEffect(()=>{load()},[])
 const create=async()=>{
  setCreating(true)
  try{const wf=await api<Workflow>('/workflows',{method:'POST',body:JSON.stringify({name:`Browser workflow ${workflows.length+1}`,target_url:url,task})});await api(`/workflows/${wf.id}/start`,{method:'POST'});load();navigate('/workspace')}catch(e){alert(String(e))}
  finally{setCreating(false)}
 }
 return <Shell><Header title="Command center" subtitle="Monitor and launch controlled browser workflows."/><div className="content">
 <div className="metrics"><Metric label="Total workflows" value={String(workflows.length)} icon={Activity}/><Metric label="Completed" value={String(workflows.filter(w=>w.status==='completed').length)} icon={CheckCircle2}/><Metric label="Active" value={String(workflows.filter(w=>w.status==='running').length)} icon={Bot}/><Metric label="Pending approvals" value={String(pendingApprovals)} icon={ClipboardCheck}/></div>
 <div className="two-col"><section className="panel quick"><h2>Quick-start workflow</h2><label>Target website<div className="input-icon"><Globe2/><input value={url} onChange={e=>setUrl(e.target.value)} /></div></label><label>Describe your goal<textarea value={task} onChange={e=>setTask(e.target.value)}/></label><button className="primary" onClick={create} disabled={creating}>{creating?'Starting…':'Launch AI agent'} <Bot size={17}/></button></section>
 <section className="panel"><div className="panel-title"><h2>Recent activity</h2><button onClick={load}>Refresh</button></div>{workflows.length?workflows.slice(0,5).map(w=><div className="activity" key={w.id}><div className="activity-icon"><Bot/></div><div><b>{w.name}</b><span>{w.status} · {w.target_url.includes('127.0.0.1:8000/sandbox')?'Local sandbox':'Public target'}</span></div><time>Now</time></div>):<Empty text="No workflows yet. Launch one to begin."/>}</section></div></div></Shell>
}
function Metric({label,value,icon:Icon}:{label:string,value:string,icon:any}){return <div className="metric"><div className="metric-icon"><Icon/></div><div><span>{label}</span><strong>{value}</strong></div></div>}

function Workspace(){
 const [log,setLog]=useState<any[]>([])
 useEffect(()=>{api<any[]>('/audit-logs').then(setLog).catch(()=>{})},[])
 return <Shell><Header title="AI Agent Workspace" subtitle="Seven-stage, evidence-driven browser orchestration."/><div className="content">
 <div className="pipeline-panel">{['USER GOAL','ORCHESTRATOR','PLANNER','POLICY GATE','BROWSER ENGINE','VALIDATION','DELIVERY'].map((x,i)=><div key={x} className={i<4?'done':i===4?'active':''}><span>{i+1}</span><b>{x}</b></div>)}</div>
 <div className="two-col"><section className="panel"><h2>Execution stream</h2>{log.slice(0,8).map((x,i)=><div className="stream" key={i}><CheckCircle2/><div><b>{x.action.replaceAll('_',' ')}</b><span>{x.detail}</span></div></div>)}{!log.length&&<Empty text="Start a workflow to see execution events."/>}</section>
 <section className="panel guard"><h2>Policy gate</h2><Rule>Public HTTP(S) and sandbox targets</Rule><Rule>Structured browser locators</Rule><Rule>Final submission locked</Rule><Rule>Human approval required</Rule></section></div></div></Shell>
}
function Rule({children}:{children:ReactNode}){return <div className="rule"><ShieldCheck/><span>{children}</span><b>Active</b></div>}

function BrowserView(){
 const [target,setTarget]=useState('http://127.0.0.1:8000/sandbox')
 useEffect(()=>{api<Workflow[]>('/workflows').then(rows=>{if(rows[0]?.target_url)setTarget(rows[0].target_url)}).catch(()=>{})},[])
 const framedTarget=target.includes('127.0.0.1:8000/sandbox')?'/sandbox/?v=20261124':target
 return <Shell><Header title="Browser Automation Viewport" subtitle="Live view of the approved target website."/><div className="content"><div className="browser"><div className="browser-bar"><div className="dots"><i/><i/><i/></div><div className="address"><ShieldCheck/><span style={{overflow:'hidden',textOverflow:'ellipsis'}}>{target}</span></div></div><iframe title="Approved target viewport" src={framedTarget} /></div></div></Shell>
}

function Eligibility(){
 const [data,setData]=useState<any>(null)
 const [workflow,setWorkflow]=useState<Workflow|null>(null)
 useEffect(()=>{api<Workflow[]>('/workflows').then(rows=>setWorkflow(rows[0]||null)).catch(()=>{})},[])
 const analyze=async()=>{if(!workflow)return;setData(await api('/analyze-eligibility',{method:'POST',body:JSON.stringify({workflow_id:workflow.id,source_url:workflow.target_url})}))}
 return <Generic title="Eligibility Analyzer" subtitle="Rules extracted from inspected portal evidence." action={workflow?analyze:undefined} actionLabel="Analyze target">{data?<><div className="source"><Globe2/><div><b>Source evidence</b><span>{data.source_url}</span></div></div>{data.requirements.map((r:string)=><div className="document-row" key={r}><CheckCircle2/><span>{r}</span><b>Verified</b></div>)}</>:<Empty text={workflow?'No evidence analyzed for the latest workflow yet.':'Create a workflow first.'}/>}</Generic>
}
function Profile(){
 const [profile,setProfile]=useState({full_name:'Aarav Kumar',email:'aarav.kumar@example.in',mobile:'+91 98765 43210',district:'Bengaluru Urban',institution:'Fictional Karnataka Institute of Technology',percentage:'82.5'})
 return <Generic title="Applicant Profile" subtitle="Fictional test data used for safe demonstration."><div className="profile-form">
  {Object.entries(profile).map(([key,value])=><label key={key}>{key.replace('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}<input value={value} onChange={e=>setProfile({...profile,[key]:e.target.value})}/></label>)}
 </div></Generic>
}
function Documents(){const docs=['Aadhaar Card','Income certificate','SSLC / PUC or degree marks card','Caste / category certificate, if applicable','Two recommendation letters','Study or personal statement'];return <Generic title="Document Checklist" subtitle="Required evidence for Karnataka scholarship preparation.">{docs.map((d,i)=><div className="document-row" key={d}><div className="doc-icon"><FileText/></div><span>{d}</span><b>{i===0?'Ready':'Required'}</b></div>)}</Generic>}
function Prepare(){
 const [fields,setFields]=useState<any[]>([])
 const [workflow,setWorkflow]=useState<Workflow|null>(null)
 useEffect(()=>{api<Workflow[]>('/workflows').then(rows=>setWorkflow(rows[0]||null)).catch(()=>{})},[])
 const prepare=async()=>{if(!workflow)return;const r=await api<any>('/prepare-form',{method:'POST',body:JSON.stringify({workflow_id:workflow.id,target_url:workflow.target_url})});setFields(r.fields)}
 const validate=async()=>{const r=await api<any>('/validate-form',{method:'POST',body:JSON.stringify({fields:Object.fromEntries(fields.map(f=>[f.name,f.value]))})});alert(r.valid?'All fields validated successfully.':'Validation errors: '+JSON.stringify(r.errors))}
 return <Generic title="Application Form Preparation" subtitle="Review proposed values before any browser fill." action={prepare} actionLabel="Prepare values">{fields.length?<>{fields.map(f=><div className="field-row" key={f.name}><label>{f.label}<input value={f.value} onChange={e=>setFields(fields.map(x=>x.name===f.name?{...x,value:e.target.value}:x))}/></label></div>) }<button className="primary" onClick={validate}>Validate form</button></>:<Empty text="Prepare suggested form values to begin."/>}</Generic>
}
function Approval(){
 const [status,setStatus]=useState('pending')
 const [approvalId,setApprovalId]=useState<number|null>(null)
 const [execution,setExecution]=useState('')
 const [workflow,setWorkflow]=useState<Workflow|null>(null)
 useEffect(()=>{api<Workflow[]>('/workflows').then(rows=>setWorkflow(rows[0]||null)).catch(()=>{})},[])
 const create=async()=>{
  if(!workflow){setExecution('Create a workflow before requesting approval');return}
  try{
   const req=await api<any>('/approvals',{method:'POST',body:JSON.stringify({workflow_id:workflow.id,proposed_action:'Fill prepared applicant fields',reason:'Use reviewed fictional Karnataka applicant values on the selected target form.',target_url:workflow.target_url,affected_fields:{full_name:'Aarav Kumar',email:'aarav.kumar@example.in',mobile:'+91 98765 43210',district:'Bengaluru Urban',institution:'Fictional Karnataka Institute of Technology',percentage:'82.5'}})})
   setApprovalId(req.id);setStatus('pending');setExecution('')
  }catch(e){setExecution(String(e))}
 }
 const decide=async(v:'approved'|'rejected')=>{
  if(!approvalId)return
  try{
   await api(`/approvals/${approvalId}/${v==='approved'?'approve':'reject'}`,{method:'POST'})
   setStatus(v)
  }catch(e){setExecution(String(e))}
 }
 const execute=async()=>{
  if(!approvalId||status!=='approved')return
  try{const r=await api<any>(`/execute-approved?approval_id=${approvalId}`,{method:'POST'});setExecution(`Executed approved fill: ${r.filled.join(', ')}`)}
  catch(e){setExecution(String(e))}
 }
 return <Generic title="Human Approval Center" subtitle="Sensitive browser actions require explicit consent." action={create} actionLabel="Create approval request">
  <div className="approval-card"><div className="approval-top"><div><b>Fill approved form fields</b><p>Sandbox registration page</p></div><span className={status}>{status}</span></div>
   <dl><dt>Reason</dt><dd>Populate only reviewed fictional Karnataka applicant fields.</dd><dt>Target</dt><dd>{workflow?.target_url||'Create a workflow first'}</dd><dt>Affected values</dt><dd>full name, email, mobile, district, institution, percentage</dd></dl>
   <div className="approval-actions"><button className="reject" onClick={()=>decide('rejected')}>Reject</button><button className="approve" onClick={()=>decide('approved')}>Approve action</button></div>
  </div>
  {execution&&<div className="source" style={{marginTop:12}}><ShieldCheck/><div><b>Execution result</b><span>{execution}</span></div></div>}
  {status==='approved'&&approvalId&&<button className="primary" style={{marginTop:12}} onClick={execute}>Execute approved fill</button>}
 </Generic>
}
function History(){
 const [workflows,setWorkflows]=useState<Workflow[]>([])
 useEffect(()=>{api<Workflow[]>('/workflows').then(setWorkflows).catch(()=>setWorkflows([]))},[])
 return <Generic title="Workflow History" subtitle="Chronological execution and status record.">
  {workflows.length?workflows.map(w=><div className="audit-row" key={w.id}><div><Activity/><div><b>{w.name}</b><span>{w.target_url}</span></div></div><span className={`approval-${w.status}`}>{w.status}</span></div>):<Empty text="New workflows will appear here after creation."/>}
 </Generic>
}
function Audit(){
 const [logs,setLogs]=useState<any[]>([])
 useEffect(()=>{api<any[]>('/audit-logs').then(setLogs).catch(()=>{})},[])
 return <Generic title="Audit Logs" subtitle="Immutable records of agent decisions and actions.">{logs.map(l=><div className="audit-row" key={l.id}><div><Activity/><b>{l.action}</b><span>{l.detail}</span></div><time>{l.created_at||'Recorded now'}</time></div>)}{!logs.length&&<Empty text="No audit events recorded."/>}</Generic>
}
function Settings(){
 const [provider,setProvider]=useState('mock')
 useEffect(()=>{api<any>('/health').then(h=>setProvider(h.ai_provider||'mock')).catch(()=>{})},[])
 return <Generic title="Settings" subtitle="Configure provider, security, and browser preferences."><div className="settings-row"><div><b>Gemini API provider</b><span>{provider==='gemini'?'Gemini Flash is configured':'Uses mock provider until GEMINI_API_KEY is configured'}</span></div><span className="toggle on"/></div><div className="settings-row"><div><b>Human approval enforcement</b><span>Required for all browser fill actions</span></div><span className="toggle on"/></div><div className="settings-row"><div><b>Final submission lock</b><span>Submit, payment, OTP and CAPTCHA actions are blocked</span></div><span className="toggle on"/></div></Generic>
}
function Field({label,value}:{label:string,value:string}){return <label>{label}<input defaultValue={value}/></label>}
function Generic({title,subtitle,children,action,actionLabel}:{title:string;subtitle:string;children:ReactNode;action?:()=>void;actionLabel?:string}){return <Shell><Header title={title} subtitle={subtitle}/><div className="content"><section className="panel wide">{action&&<div className="panel-title"><h2>Evidence workspace</h2><button className="small-primary" onClick={action}>{actionLabel}</button></div>}{children}</section></div></Shell>}
function Empty({text}:{text:string}){return <div className="empty"><Globe2/><span>{text}</span></div>}

function PageFor({name}:{name:string}) {
  if (name === 'dashboard') return <Dashboard/>
  if (name === 'workspace') return <Workspace/>
  if (name === 'browser') return <BrowserView/>
  if (name === 'eligibility') return <Eligibility/>
  if (name === 'profile') return <Profile/>
  if (name === 'documents') return <Documents/>
  if (name === 'prepare') return <Prepare/>
  if (name === 'approval') return <Approval/>
  if (name === 'history') return <History/>
  if (name === 'audit') return <Audit/>
  return <Settings/>
}

export default function App(){return <Routes><Route path="/" element={<Landing/>}/>{nav.map(([p])=><Route key={p} path={`/${p}`} element={<PageFor name={p}/>}/>)}</Routes>}
