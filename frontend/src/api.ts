import type { Example, RenderJob, Solution, Topic } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try { res = await fetch(`/api${path}`, init) }
  catch { throw new Error('Cannot connect to the Python API. Start the backend on port 8000.') }
  if (!res.ok) {
    const data: {detail?: string} = await res.json().catch(() => ({}))
    throw new Error(data.detail || `Request failed (${res.status}).`)
  }
  return res.json() as Promise<T>
}
export const getExamples = () => request<Example[]>('/examples')
export const getHealth = () => request<{status:string; manim_enabled:boolean; manim_available:boolean}>('/health')
export const solvePhysics = (problem:string, topic:Topic|null, parameters:Record<string,number>) =>
  request<Solution>('/solve',{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({problem,topic,parameters})})
export const startRender = (id:string) => request<RenderJob>(`/render/${id}`,{method:'POST'})
export const getRender = (id:string) => request<RenderJob>(`/jobs/${id}`)
