const API_ROOT = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, "") ?? "";
const BASE = `${API_ROOT}/api/v1`;

export interface StatusResponse {
  status: string;
  version: string;
  service: string;
  product: string;
  backend_port: number;
  frontend_port: number;
  ffmpeg: boolean;
  align_available: boolean;
  providers: { llm: string[]; stock: string[]; tts: string[] };
  job_count: number;
  jobs_complete: number;
  jobs_active: number;
  tool_count: number;
}

export interface Job {
  job_id: string;
  status: string;
  progress: number;
  topic: string;
  output_path: string;
  error: string;
  created_at: string;
  updated_at: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  kind: string;
}

export interface PublishPack {
  success: boolean;
  job_id: string;
  ready: boolean;
  title: string;
  caption: string;
  hashtags: string[];
  output_path: string;
  download_url: string;
  platforms: PlatformInfo[];
  recommended_platforms: PlatformInfo[];
  workflow: string[];
  future_api: Record<string, string>;
  message?: string;
}

export interface PlatformInfo {
  id: string;
  label: string;
  upload_url: string;
  creator_url: string;
  aspect: string;
  max_short_s: number;
  api_tier: string;
  notes: string;
}

export interface Storyboard {
  title: string;
  total_scenes: number;
  planned_duration: number;
  chapters: { title: string; scenes: unknown[] }[];
}

export async function getStatus(): Promise<StatusResponse> {
  const res = await fetch(`${API_ROOT || ""}/api/v1/status`);
  if (!res.ok) throw new Error(`Status ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch(`${API_ROOT || ""}/health`);
  return res.json();
}

export async function getTools(): Promise<{ tools: ToolInfo[]; count: number }> {
  const res = await fetch(`${BASE}/tools`);
  return res.json();
}

export async function listJobs(limit = 20): Promise<{ jobs: Job[]; count: number }> {
  const res = await fetch(`${BASE}/jobs?limit=${limit}`);
  return res.json();
}

export async function getJob(jobId: string): Promise<{ job: Job }> {
  const res = await fetch(`${BASE}/jobs/${jobId}`);
  return res.json();
}

export async function generateVideo(body: {
  topic?: string;
  script?: string | null;
  aspect?: string;
  voice?: string;
  clip_duration?: number;
  paragraph_count?: number;
}): Promise<{ job_id: string; status: string }> {
  const res = await fetch(`${BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function planVideo(body: {
  topic: string;
  video_type?: string;
  target_duration?: number;
  language?: string;
  chapters?: number;
  style_notes?: string;
}): Promise<{ storyboard: Storyboard }> {
  const res = await fetch(`${BASE}/plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function planRender(body: {
  topic: string;
  video_type?: string;
  target_duration?: number;
  aspect?: string;
  language?: string;
  voice?: string;
  chapters?: number;
}): Promise<{ job_id: string; status: string }> {
  const params = new URLSearchParams();
  Object.entries(body).forEach(([k, v]) => {
    if (v !== undefined && v !== "") params.set(k, String(v));
  });
  const res = await fetch(`${BASE}/plan/render?${params}`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getPublishPack(jobId: string): Promise<PublishPack> {
  const res = await fetch(`${BASE}/jobs/${jobId}/publish-pack`);
  return res.json();
}

export async function revealJob(jobId: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${BASE}/jobs/${jobId}/reveal`, { method: "POST" });
  return res.json();
}

export function downloadUrl(jobId: string): string {
  return `${API_ROOT}/api/v1/jobs/${jobId}/download`;
}

export async function probeOllama(): Promise<boolean> {
  try {
    const res = await fetch("http://127.0.0.1:11434/api/tags", { signal: AbortSignal.timeout(1500) });
    return res.ok;
  } catch {
    return false;
  }
}
