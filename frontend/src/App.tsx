import { useEffect, useMemo, useState } from 'react'
import {
  Atom, BookOpen, Braces, Check, CheckCheck, CheckCircle2, ChevronDown,
  CircleHelp, Clipboard, Clock3, Code2, Download, ExternalLink, FileCheck2, FileCode2,
  FlaskConical, Loader2, Menu, Play, RefreshCw, Settings2,
  ShieldCheck, Sparkles, WandSparkles, X, Zap
} from 'lucide-react'
import PhysicsPreview from './components/PhysicsPreview'
import { getExamples, getHealth, getRender, solvePhysics, startRender } from './api'
import type { Example, RenderJob, Solution, Tab, Topic } from './types'

const fallbacks: Example[] = [
  {topic:'spring',title:'Simple Harmonic Motion', problem:'A 2 kg block is attached to a spring of constant 50 N/m on a frictionless surface. It is displaced by 0.2 m and released. Find the period and animate the oscillation.', parameters:{mass:2,k:50,amplitude:.2}},
  {topic:'projectile',title:'Projectile Motion',problem:'A ball is launched at 20 m/s at an angle of 45 degrees above the horizontal. Calculate its flight time, maximum height, and range, then visualize the trajectory.', parameters:{speed:20,angle_deg:45}},
  {topic:'incline',title:'Inclined Plane',problem:'A 5 kg block slides down a frictionless incline at 30 degrees to the horizontal. Determine its acceleration and the distance after 3 seconds from rest.', parameters:{mass:5,angle_deg:30,time:3}},
  {topic:'pendulum',title:'Simple Pendulum',problem:'A simple pendulum of length 1.5 m is released from 12 degrees. Estimate its small-angle oscillation period and visualize its motion.', parameters:{length:1.5,angle_deg:12}}
]
const prettyKey:Record<string,string> = {mass:'Mass (kg)',k:'Spring constant (N/m)',amplitude:'Amplitude (m)',speed:'Initial speed (m/s)',angle_deg:'Angle (degrees)',time:'Time (s)',length:'Length (m)'}
const outputKeys:Record<string,string> = {
  angular_frequency_rad_s:'Angular frequency',period_s:'Period',max_speed_m_s:'Max speed',
  flight_time_s:'Flight time',range_m:'Range',max_height_m:'Maximum height',
  acceleration_m_s2:'Acceleration',distance_m:'Distance',final_speed_m_s:'Final speed'
}
const unit:Record<string,string> = {angular_frequency_rad_s:'rad/s',period_s:'s',max_speed_m_s:'m/s',flight_time_s:'s',range_m:'m',max_height_m:'m',acceleration_m_s2:'m/s²',distance_m:'m',final_speed_m_s:'m/s'}
const illustrations:Record<Topic,string> = {spring:'〰️',projectile:'↗',incline:'◢',pendulum:'◉'}

function downloadText(text:string, fileName:string) {
  const href = URL.createObjectURL(new Blob([text],{type:'text/x-python;charset=utf-8'}))
  const anchor = document.createElement('a'); anchor.href=href; anchor.download=fileName; anchor.click()
  URL.revokeObjectURL(href)
}

export default function App() {
  const [examples,setExamples] = useState<Example[]>(fallbacks)
  const [selected,setSelected] = useState<Topic>('spring')
  const [problem,setProblem] = useState(fallbacks[0].problem)
  const [parameters,setParameters] = useState<Record<string,number>>(fallbacks[0].parameters)
  const [solution,setSolution] = useState<Solution|null>(null)
  const [tab,setTab] = useState<Tab>('solution')
  const [loading,setLoading] = useState(false)
  const [error,setError] = useState('')
  const [online,setOnline] = useState(false)
  const [canRender,setCanRender] = useState(false)
  const [render,setRender] = useState<RenderJob|null>(null)
  const [menu,setMenu] = useState(false)
  const [about,setAbout] = useState(false)
  const [copied,setCopied] = useState(false)
  const sample = useMemo(()=> examples.find(e=>e.topic===selected)||fallbacks[0],[selected,examples])
  const currentTopic = solution?.topic||selected
  const previewParams = solution?.parameters||parameters

  useEffect(()=>{
    getExamples().then(setExamples).catch(()=>{})
    getHealth().then(x=>{setOnline(true);setCanRender(x.manim_available&&x.manim_enabled)}).catch(()=>setOnline(false))
  },[])
  useEffect(()=>{
    if (!render || !['queued','running'].includes(render.status)) return
    const timer=setInterval(()=>{getRender(render.job_id).then(setRender).catch(e=>setError(e.message))},1600)
    return ()=>clearInterval(timer)
  },[render])

  function choose(example:Example) {
    setSelected(example.topic);setProblem(example.problem);setParameters(example.parameters)
    setSolution(null);setError('');setTab('solution');setRender(null)
  }
  async function runSolve() {
    setLoading(true);setError('');setRender(null)
    try { const data=await solvePhysics(problem,selected,parameters);setOnline(true);setSolution(data);setTab('solution') }
    catch(e) { setError(e instanceof Error?e.message:String(e)) }
    finally {setLoading(false)}
  }
  async function doRender() {
    if (!solution) return
    setError('')
    try{setRender(await startRender(solution.id))}
    catch(e){setError(e instanceof Error?e.message:String(e))}
  }
  async function copyCode() {
    if(!solution)return
    try{await navigator.clipboard.writeText(solution.manim_code);setCopied(true);window.setTimeout(()=>setCopied(false),1600)}
    catch {setError('Clipboard permission unavailable. Use Download Python instead.')}
  }
  const passes=solution?.checks.filter(c=>c.passed).length||0

  return <>
    <header className="topbar">
      <div className="brand"><div className="brand-icon"><Atom size={27} strokeWidth={2.4}/></div><span>PhysicsSolution<span className="brand-highlight">Agent</span></span></div>
      <button className="mobile-menu" onClick={()=>setMenu(!menu)} aria-label="Toggle navigation">{menu?<X/>:<Menu/>}</button>
      <nav className={menu?'nav-links open':'nav-links'}>
        <a className="active" href="#home" onClick={()=>setMenu(false)}>Home</a>
        <a href="#how-it-works" onClick={()=>setMenu(false)}>How it works</a>
        <a href="#examples" onClick={()=>setMenu(false)}>Examples</a>
        <a href="#evaluation" onClick={()=>{setTab('evaluation');setMenu(false)}}>Evaluation</a>
        <button onClick={()=>{setAbout(true);setMenu(false)}}>About</button>
      </nav>
      <div className="header-right"><div className="connection" title="Live backend status"><i className={online?'online':'offline'}/>{online?'API connected':'Demo mode'}</div><span className="avatar">V</span><span className="user-name">Vinayak</span></div>
    </header>

    <main className="app-layout" id="home">
      <section className="left-panel">
        <div className="hero">
          <div className="eyebrow"><Sparkles size={15}/> FROM PHYSICS PROBLEM TO ANIMATION</div>
          <h1>Solve. Visualize. <span>Learn.</span></h1>
          <p>Explore physics with verified calculations, clear explanations, and executable Manim animations — all from one workspace.</p>
          <div className="workflow" id="how-it-works">
            <div className="workflow-unit"><div className="work-ico blue"><FileCheck2 size={19}/></div><span>Understand<br/>problem</span></div>
            <div className="flow-arrow">→</div>
            <div className="workflow-unit"><div className="work-ico purple"><FlaskConical size={19}/></div><span>Calculate<br/>physics</span></div>
            <div className="flow-arrow">→</div>
            <div className="workflow-unit"><div className="work-ico blue"><Code2 size={19}/></div><span>Generate<br/>Manim</span></div>
            <div className="flow-arrow">→</div>
            <div className="workflow-unit"><div className="work-ico green"><CheckCheck size={19}/></div><span>Verify<br/>results</span></div>
          </div>
        </div>

        <section className="card input-card">
          <div className="card-heading"><div className="heading-left"><FileCode2 size={22}/><h2>Enter a Physics Problem</h2></div><div className="level-chip">Undergraduate <ChevronDown size={14}/></div></div>
          <div className="form-label-row"><label htmlFor="topic">Supported scenario</label><span className="help-text">4 verified mechanics templates</span></div>
          <select id="topic" value={selected} onChange={e=>{const ex=examples.find(x=>x.topic===e.target.value);if(ex)choose(ex)}}>
            {examples.map(ex=><option key={ex.topic} value={ex.topic}>{ex.title}</option>)}
          </select>
          <label htmlFor="problem" className="field-label">Problem statement</label>
          <textarea id="problem" spellCheck={true} rows={5} value={problem} onChange={e=>setProblem(e.target.value)} placeholder="Describe a supported physics scenario..."/>
          <div className="param-header"><div className="heading-left"><Settings2 size={15}/><strong>Physical parameters</strong></div><span>Editable · SI units</span></div>
          <div className="params-grid">
            {Object.keys(sample.parameters).map(key=><label className="parameter" key={key}>{prettyKey[key]||key}<input type="number" step="any" value={parameters[key]??''} onChange={e=>setParameters(old=>({...old,[key]:Number(e.target.value)}))} /></label>)}
          </div>
          {error && <div role="alert" className="error"><CircleHelp size={16}/><span>{error}</span></div>}
          <div className="action-row"><button type="button" className="action-secondary" onClick={()=>choose(sample)}><RefreshCw size={16}/> Reset example</button><button type="button" className="action-primary" disabled={loading} onClick={runSolve}>{loading?<Loader2 className="spin" size={18}/>:<WandSparkles size={18}/>} {loading?'Solving…':'Generate Solution'}</button></div>
          <p className="honesty-note"><ShieldCheck size={13}/> This starter uses checked equations; it does not infer arbitrary physics from prose.</p>
        </section>

        <section className="card examples-card" id="examples"><div className="card-heading"><div className="heading-left"><BookOpen size={22}/><h2>Example Problems</h2></div><span className="examples-count">4 topics</span></div>
          <div className="examples-grid">{examples.map(ex=><button type="button" key={ex.topic} onClick={()=>choose(ex)} className={`example ${selected===ex.topic?'selected':''}`}>
            <span className="example-drawing">{illustrations[ex.topic]}</span><strong>{ex.title}</strong><small>{ex.topic==='spring'?'Oscillating block and Hooke’s law':ex.topic==='projectile'?'Launch velocity, range and height':ex.topic==='incline'?'Forces, acceleration and motion':'Small-angle pendulum dynamics'}</small><span className="try">Try this →</span>
          </button>)}</div>
        </section>
        <div className="bottom-tip"><Zap size={17}/> <span><b>Tip:</b> Run the backend to calculate solutions. Manim MP4 rendering is optional and requires local installation.</span></div>
      </section>

      <section className="right-panel">
        <div className="card output-card"><div className="output-heading"><div className="heading-left"><div className="output-ico"><FileCheck2 size={22}/></div><h2>Generated Solution & Animation</h2></div><div className={`status-chip ${solution?'success':''}`}>{solution?<><Check size={13}/> Calculated & checked</>:<><Clock3 size={13}/> Ready to solve</>}</div></div>
          {render?.status==='complete'&&render.video_url?<div className="rendered-video"><video controls src={render.video_url} /></div>:<PhysicsPreview topic={currentTopic} parameters={previewParams}/>}
          <div className="video-bar"><span><div className="live-dot"/> {solution?'Result available':'Live example visualization'}</span><span>{solution?'Manim code generated':'Select an example and generate'}</span></div>
          {solution&&<div className="result-summary"><span className="summary-icon"><CheckCircle2 size={16}/></span><span>{solution.summary}</span></div>}
          <div className="tab-list" role="tablist" aria-label="Solution view">
            <button role="tab" aria-selected={tab==='solution'} className={tab==='solution'?'active':''} onClick={()=>setTab('solution')}><BookOpen size={16}/> Step-by-Step</button>
            <button role="tab" aria-selected={tab==='code'} className={tab==='code'?'active':''} onClick={()=>setTab('code')}><Braces size={16}/> Generated Code</button>
            <button role="tab" aria-selected={tab==='evaluation'} className={tab==='evaluation'?'active':''} onClick={()=>setTab('evaluation')}><FileCheck2 size={16}/> Verification</button>
          </div>
          {tab==='solution' && <div className="steps">
            {(solution?.steps||[
              {title:'Model the system',explanation:'Choose an example and generate a solution to calculate the physical quantities.',formula:'F = ma'},
              {title:'Apply the physical laws',explanation:'Known quantities and assumptions are matched to a verified physics template.',formula:'Model + assumptions'},
              {title:'Calculate quantities',explanation:'The Python backend computes numerical answers deterministically.',formula:'Numerical solution'},
              {title:'Generate animation code',explanation:'The service creates a Manim scene from the verified template.',formula:'Python → Manim Scene'}
            ]).map((step,index)=><div className="step" key={index}><div className={`step-number color-${index}`}>{index+1}</div><div className="step-info"><span className="step-pill">STEP {index+1}</span><strong>{step.title}</strong><p>{step.explanation}</p><div className="formula">{step.formula}</div></div></div>)}
          </div>}
          {tab==='code'&&<div className="code-tab">{solution?<><div className="code-toolbar"><span>scene.py · {solution.scene_name}</span><div><button onClick={copyCode}>{copied?<Check size={14}/>:<Clipboard size={14}/>} {copied?'Copied':'Copy'}</button><button onClick={()=>downloadText(solution.manim_code,`${solution.topic}_scene.py`)}><Download size={14}/> Download .py</button></div></div><pre><code>{solution.manim_code}</code></pre></>:<div className="empty"><Code2 size={40}/><h3>No generated code yet</h3><p>Generate a solution to view the corresponding Manim scene.</p></div>}</div>}
          {tab==='evaluation'&&<div className="evaluation-tab" id="evaluation"><div className="eval-heading"><ShieldCheck size={20}/><div><strong>Deterministic verification</strong><p>15 programmatic checks — not the resume’s 15-stage VLM benchmark.</p></div><div className="pass-score">{solution?`${passes}/15`:'—/15'}</div></div>
            {solution?<><div className="checks-list">{solution.checks.map((check,index)=><div key={index} className="check"><CheckCircle2 size={17} className={check.passed?'ok':'fail'}/><div><strong>{check.name}</strong><small>{check.detail}</small></div></div>)}</div></>:<div className="empty"><ShieldCheck size={38}/><h3>Ready for verification</h3><p>Run a problem to see the actual checks performed by the backend.</p></div>}</div>}
          {solution&&<div className="output-actions"><div className="computed-values">{Object.entries(solution.result).slice(0,3).map(([key,value])=><div key={key}><small>{outputKeys[key]||key}</small><strong>{typeof value==='number'?Number(value).toFixed(2):String(value)} <span>{unit[key]||''}</span></strong></div>)}</div><div className="render-btn-wrap"><button className="render-btn" disabled={!canRender||render?.status==='running'||render?.status==='queued'} onClick={doRender}>{render?.status==='running'?<Loader2 size={16} className="spin"/>:<Play size={16}/>} {render?.status==='running'?'Rendering…':'Render MP4 (Manim)'}</button><small>{!canRender?'Enable Manim in the backend to export video.':render?.message||'Render a video from vetted templates.'}</small></div></div>}
        </div>
        <aside className="disclaimer"><div><ShieldCheck size={18}/><strong>Designed for transparent reasoning</strong></div><p>Actual computations, explicit assumptions, and source-code output. No untrusted AI-generated Python code is executed.</p></aside>
      </section>
    </main>
    <footer><span>⚛ PhysicsSolutionAgent · Open-source starter</span><span>Python · FastAPI · React · Manim</span><a href="https://www.manim.community/" target="_blank" rel="noreferrer">Manim Community <ExternalLink size={13}/></a></footer>
    {about&&<div className="modal-backdrop" role="presentation" onClick={()=>setAbout(false)}><div className="modal" role="dialog" aria-modal="true" aria-label="About PhysicsSolutionAgent" onClick={e=>e.stopPropagation()}><button className="modal-close" aria-label="Close" onClick={()=>setAbout(false)}><X/></button><Atom size={40} color="#5664ed"/><h2>About PhysicsSolutionAgent</h2><p>This working starter calculates four introductory mechanics problems with numerical solvers, builds safe Manim scene templates, and displays programmatic verification checks.</p><p>Arbitrary problem solving and vision-language-model evaluation are not implemented. Those are research extensions, not demonstrated capabilities.</p><button className="action-primary" onClick={()=>setAbout(false)}>Got it</button></div></div>}
  </>
}
