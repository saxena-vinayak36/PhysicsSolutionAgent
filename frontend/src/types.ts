export type Topic = 'spring' | 'projectile' | 'incline' | 'pendulum'
export type Tab = 'solution' | 'code' | 'evaluation'
export interface Example { topic: Topic; title: string; problem: string; parameters: Record<string, number> }
export interface SolutionStep { title: string; explanation: string; formula: string }
export interface CheckResult { name: string; passed: boolean; detail: string }
export interface Solution {
  id: string; topic: Topic; title: string; summary: string; problem: string
  parameters: Record<string, number>; result: Record<string, number|string>; steps: SolutionStep[]
  manim_code: string; scene_name: string; checks: CheckResult[]; validation_note: string
}
export interface RenderJob { job_id: string; status: 'queued'|'running'|'complete'|'failed'; message: string; video_url: string|null }
