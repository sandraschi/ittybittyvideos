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
  llm?: {
    configured_provider: string;
    openai_key_set: boolean;
    openai_ready: boolean;
    deepseek_key_set: boolean;
    deepseek_ready: boolean;
    deepseek_model: string;
    lmstudio_ready: boolean;
    lmstudio_model: string | null;
    lmstudio_base_url: string;
    ollama_reachable: boolean;
    ollama_ready: boolean;
    ready_for_topics: boolean;
    hint: string;
  };
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
  llm_provider?: string;
  aspect?: string;
  voice?: string;
  clip_duration?: number;
  paragraph_count?: number;
  visual_style?: string;
  visual_material?: string;
  visual_tone?: string;
  structure?: string;
  style_notes?: string;
  intro?: string;
}): Promise<{ job_id: string; status: string }> {
  const res = await fetch(`${BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    try {
      const parsed = JSON.parse(text) as { detail?: string };
      throw new Error(parsed.detail ?? text);
    } catch (e) {
      if (e instanceof Error && e.message !== text) throw e;
      throw new Error(text || `Generate failed (${res.status})`);
    }
  }
  return res.json();
}

export async function planVideo(body: {
  topic: string;
  video_type?: string;
  target_duration?: number;
  language?: string;
  chapters?: number;
  style_notes?: string;
  visual_style?: string;
  visual_material?: string;
  visual_tone?: string;
  structure?: string;
  intro?: string;
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
  style_notes?: string;
  structure?: string;
  intro?: string;
  visual_style?: string;
  visual_material?: string;
  visual_tone?: string;
}): Promise<{ job_id: string; status: string }> {
  const params = new URLSearchParams();
  Object.entries(body).forEach(([k, v]) => {
    if (v !== undefined && v !== "") params.set(k, String(v));
  });
  const res = await fetch(`${BASE}/plan/render?${params}`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export interface DepotItem {
  job_id: string;
  topic: string;
  status: string;
  progress: number;
  file_size_mb: number;
  created_at: string;
  updated_at: string;
  source: string;
  has_file: boolean;
  download_url: string;
  publish_url: string;
  poster_url: string;
  error: string;
}

export interface DepotSummary {
  output_dir: string;
  db_path: string;
  total: number;
  on_disk: number;
  imported: number;
}

export async function listDepot(limit = 100): Promise<{
  success: boolean;
  summary: DepotSummary;
  items: DepotItem[];
  count: number;
}> {
  const res = await fetch(`${BASE}/depot?limit=${limit}`);
  if (!res.ok) throw new Error(`Depot ${res.status}`);
  return res.json();
}

export async function scanDepot(): Promise<{
  success: boolean;
  summary: DepotSummary;
  items: DepotItem[];
  message: string;
}> {
  const res = await fetch(`${BASE}/depot/scan`, { method: "POST" });
  if (!res.ok) throw new Error(`Scan ${res.status}`);
  return res.json();
}

export async function deleteDepotItem(jobId: string, deleteFile = true): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${BASE}/depot/${jobId}?delete_file=${deleteFile ? "true" : "false"}`, {
    method: "DELETE",
  });
  return res.json();
}

export function posterUrl(jobId: string): string {
  return `${API_ROOT}/api/v1/depot/${jobId}/poster`;
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

export const SECRET_MASK = "••••••••";

export interface ProviderSettings {
  id: string;
  label: string;
  ready: boolean;
  model: string;
  base_url: string;
  api_key_set: boolean;
  api_key_hint: string;
}

export interface LlmDiscovery {
  provider: string;
  available: boolean;
  error: string;
  models: string[];
  selected_model: string;
}

export interface AppSettings {
  env_path: string;
  videogen_llm_provider: string;
  llm_providers: ProviderSettings[];
  videogen_stock_provider: string;
  pexels_api_key_set: boolean;
  pexels_api_key_hint: string;
  cogvideo_url: string;
  cogvideo_ready: boolean;
  cogvideo_error: string;
  google_api_key_set: boolean;
  google_api_key_hint: string;
  google_cloud_project: string;
  google_ai_mcp_url: string;
  veo_ready: boolean;
  omni_ready: boolean;
  jellyfin_server_url?: string;
  jellyfin_api_key_set?: boolean;
  jellyfin_api_key_hint?: string;
  plex_url?: string;
  plex_token_set?: boolean;
  plex_token_hint?: string;
  stock_ready_for_renders: boolean;
  stock_hint: string;
  videogen_tts_provider: string;
  edge_tts_voice: string;
}

export interface SettingsBundle {
  success: boolean;
  settings: AppSettings;
  models: LlmDiscovery[];
  secret_mask: string;
}

export interface SettingsSavePayload {
  videogen_llm_provider?: string;
  deepseek_api_key?: string;
  deepseek_base_url?: string;
  deepseek_model?: string;
  openai_api_key?: string;
  openai_base_url?: string;
  openai_model?: string;
  lmstudio_base_url?: string;
  lmstudio_api_key?: string;
  lmstudio_model?: string;
  ollama_base_url?: string;
  ollama_model?: string;
  pexels_api_key?: string;
  cogvideo_url?: string;
  google_api_key?: string;
  google_cloud_project?: string;
  google_cloud_location?: string;
  google_ai_mcp_url?: string;
  google_veo_model?: string;
  google_omni_model?: string;
  jellyfin_server_url?: string;
  jellyfin_api_key?: string;
  plex_url?: string;
  plex_token?: string;
  videogen_stock_provider?: string;
  videogen_tts_provider?: string;
  edge_tts_voice?: string;
}

export async function getSettings(): Promise<SettingsBundle> {
  const res = await fetch(`${BASE}/settings`);
  if (!res.ok) throw new Error(`Settings ${res.status}`);
  return res.json();
}

export async function refreshModels(provider?: string): Promise<LlmDiscovery | LlmDiscovery[]> {
  const q = provider ? `?provider=${encodeURIComponent(provider)}` : "";
  const res = await fetch(`${BASE}/settings/models${q}`);
  if (!res.ok) throw new Error(`Models ${res.status}`);
  const data = await res.json();
  if (provider) return data.discovery as LlmDiscovery;
  return data.discoveries as LlmDiscovery[];
}

export async function refreshStockStatus(): Promise<{
  success: boolean;
  stock: {
    active_provider: string;
    ready_for_renders: boolean;
    pexels_ready: boolean;
    cogvideo_url: string;
    cogvideo_ready: boolean;
    cogvideo_error: string;
    veo_ready?: boolean;
    omni_ready?: boolean;
    jellyfin_ready?: boolean;
    plex_ready?: boolean;
    hint: string;
  };
}> {
  const res = await fetch(`${BASE}/settings/stock`);
  if (!res.ok) throw new Error(`Stock status ${res.status}`);
  return res.json();
}

export async function saveSettings(body: SettingsSavePayload): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${BASE}/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    try {
      const parsed = JSON.parse(text) as { detail?: string };
      throw new Error(parsed.detail ?? text);
    } catch (e) {
      if (e instanceof Error && e.message !== text) throw e;
      throw new Error(text || `Save failed (${res.status})`);
    }
  }
  return res.json();
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  kind: string;
  detail: string;
  meta?: Record<string, unknown>;
}

export interface LogQueryResult {
  entries: LogEntry[];
  total: number;
  limit: number;
  offset: number;
  max_entries: number;
  sort: string;
}

export interface LogQueryParams {
  limit?: number;
  offset?: number;
  level?: string;
  kind?: string;
  search?: string;
  sort?: "asc" | "desc";
  after_id?: string;
}

function logsQueryString(params: LogQueryParams): string {
  const q = new URLSearchParams();
  if (params.limit != null) q.set("limit", String(params.limit));
  if (params.offset != null) q.set("offset", String(params.offset));
  if (params.level) q.set("level", params.level);
  if (params.kind) q.set("kind", params.kind);
  if (params.search) q.set("search", params.search);
  if (params.sort) q.set("sort", params.sort);
  if (params.after_id) q.set("after_id", params.after_id);
  const s = q.toString();
  return s ? `?${s}` : "";
}

export async function queryLogs(params: LogQueryParams = {}): Promise<LogQueryResult> {
  const res = await fetch(`/api/logs${logsQueryString(params)}`);
  if (!res.ok) throw new Error(`Logs ${res.status}`);
  return res.json();
}

export async function getLogStats(): Promise<Record<string, unknown>> {
  const res = await fetch("/api/logs/stats");
  if (!res.ok) throw new Error(`Log stats ${res.status}`);
  return res.json();
}

export async function clearLogs(): Promise<void> {
  const res = await fetch("/api/logs", { method: "DELETE" });
  if (!res.ok) throw new Error(`Clear logs ${res.status}`);
}

export async function exportLogsJson(params: LogQueryParams = {}): Promise<void> {
  const extra = logsQueryString(params);
  const join = extra ? `${extra}&format=json` : "?format=json";
  const res = await fetch(`/api/logs/export${join}`);
  if (!res.ok) throw new Error(`Export logs ${res.status}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "ittybitty-logs.json";
  a.click();
  URL.revokeObjectURL(url);
}
