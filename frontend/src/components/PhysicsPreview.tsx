import { useEffect, useState } from 'react'
import type { Topic } from '../types'

interface Props { topic: Topic; parameters: Record<string,number> }

export default function PhysicsPreview({topic, parameters}:Props) {
  const [tick,setTick] = useState(0)
  const [playing,setPlaying] = useState(true)
  useEffect(()=> {
    if (!playing) return
    let id = 0
    let last = 0
    const animate = (now:number) => { if (now-last>30) { setTick(x=>x+0.035); last=now } id=requestAnimationFrame(animate) }
    id=requestAnimationFrame(animate)
    return ()=>cancelAnimationFrame(id)
  },[playing])
  const label = {spring:'Simple Harmonic Motion', projectile:'Projectile Motion',incline:'Inclined Plane',pendulum:'Simple Pendulum'}[topic]
  const phase = Math.sin(tick*2.3)
  const svgCommon = {viewBox:'0 0 660 350', role:'img' as const, 'aria-label':`Animated diagram: ${label}`}
  return <div className="physics-preview">
    <div className="preview-header"><span className="preview-pulse"/> Interactive physics preview <span className="preview-mode">SVG SIMULATION</span></div>
    <svg {...svgCommon}>
      <defs>
        <linearGradient id="block" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#79b8ff"/><stop offset="1" stopColor="#3473ed"/></linearGradient>
        <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#65758e"/><stop offset="1" stopColor="#384458"/></linearGradient>
        <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M 32 0 L 0 0 0 32" fill="none" stroke="#243144" strokeWidth=".7" opacity=".35"/></pattern>
      </defs>
      <rect width="660" height="350" fill="#0d1421"/><rect width="660" height="350" fill="url(#grid)"/>
      <text x="330" y="39" fontSize="20" fontWeight="500" fill="#eff5ff" textAnchor="middle">{label}</text>
      {topic==='spring' && (()=>{
        const cx=355+phase*55
        const start=103, end=cx-35
        const pts=Array.from({length:33},(_,i)=>`${start+(end-start)*(i/32)},${189+(i===0||i===32?0:(i%2===0?10:-10))}`).join(' ')
        return <g><rect x="74" y="128" width="14" height="145" fill="#8b99b1"/><rect x="73" y="247" width="516" height="16" fill="url(#floor)"/>
          <polyline points={pts} fill="none" stroke="#f4c35c" strokeWidth="3"/>
          <rect x={cx-35} y="152" width="70" height="70" fill="url(#block)" rx="5"/>
          <text x={cx} y="194" textAnchor="middle" fontSize="22" fill="#e9f3ff" fontStyle="italic">m</text>
          <path d="M 460 192 L 555 192" stroke="#e9f3ff" strokeWidth="1.4" strokeDasharray="5 6"/>
          <text x="330" y="314" textAnchor="middle" fill="#cbd8f2" fontSize="21" fontStyle="italic">T = 2π √(m / k)</text>
          <text x="137" y="145" fill="#f2cb73" fontSize="17">k = {parameters.k||50} N/m</text></g>
      })()}
      {topic==='projectile' && (()=>{
        const progress = ((tick*.20)%1)
        const x=85+progress*490
        const y=272-Math.sin(progress*Math.PI)*170
        return <g><line x1="76" y1="274" x2="607" y2="274" stroke="#71839e" strokeWidth="2"/><line x1="85" y1="292" x2="85" y2="65" stroke="#71839e" strokeWidth="2"/>
          <path d="M85 274 Q 330 -65 575 274" fill="none" stroke="#8bb7fb" strokeDasharray="7 6" strokeWidth="2.5"/>
          <circle cx={x} cy={y} r="12" fill="#f8bc59"/><circle cx={x-4} cy={y-4} r="3" fill="#ffeba6"/>
          <text x="360" y="316" fill="#cddcf8" fontSize="19" textAnchor="middle">v₀ = {parameters.speed||20} m/s  ·  θ = {parameters.angle_deg||45}°</text>
          <text x="577" y="295" fill="#9aacca" fontSize="14">range</text></g>
      })()}
      {topic==='incline' && (()=>{
        const angle = Math.min(75,parameters.angle_deg||30)
        const p = (tick*.18)%1
        const endX=540, endY=278, startY=278-(380*Math.tan(angle*Math.PI/180))
        const normY = Math.max(75, startY)
        const bx=160+(endX-160)*p, by=normY+(endY-normY)*p
        return <g><path d={`M 160 ${normY} L ${endX} ${endY} L 160 ${endY} Z`} fill="#223653" stroke="#a0b7d8" strokeWidth="3"/>
          <rect x={bx-25} y={by-39} width="49" height="47" rx="5" fill="url(#block)" transform={`rotate(${Math.atan2(endY-normY,endX-160)*180/Math.PI} ${bx} ${by})`}/>
          <path d="M 486 285 A 55 55 0 0 0 440 257" stroke="#e9bd65" fill="none" strokeWidth="2"/>
          <text x="471" y="247" fill="#f1ca7a" fontSize="18">θ</text>
          <text x="330" y="329" textAnchor="middle" fill="#cbdcf8" fontSize="20">a = g sin({angle}°)</text></g>
      })()}
      {topic==='pendulum' && (()=>{
        const theta=(parameters.angle_deg||12)*Math.PI/180
        const cx=330+Math.sin(tick*2)*Math.sin(theta)*340,cy=100+Math.cos(Math.asin((cx-330)/340))*204
        return <g><line x1="250" x2="410" y1="98" y2="98" stroke="#889bb5" strokeWidth="8"/>
          <path d="M 330 100 L 330 310" stroke="#a5bfd6" strokeDasharray="5 6" opacity=".5"/>
          <path d={`M 330 100 L ${cx} ${cy}`} stroke="#b5c4da" strokeWidth="4"/><circle cx={cx} cy={cy} r="20" fill="url(#block)"/>
          <circle cx="330" cy="100" r="6" fill="#e3ebfa"/><text x="330" y="333" fontSize="20" textAnchor="middle" fill="#cbdcf8">T = 2π √(L / g)</text></g>
      })()}
    </svg>
    <div className="preview-controls"><button type="button" onClick={()=>setPlaying(!playing)} aria-label={playing?'Pause preview':'Play preview'}>{playing?'Ⅱ':'▶'}</button><span>{playing?'Simulating':'Paused'}</span><div className="preview-track"><span/></div><span>Interactive model · not a rendered video</span></div>
  </div>
}
