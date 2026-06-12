import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Eye, EyeOff } from "lucide-react";
import {
  getSettings,
  refreshModels,
  refreshStockStatus,
  saveSettings,
  SECRET_MASK,
  type LlmDiscovery,
  type SettingsSavePayload,
} from "@/lib/api";

type ProviderId = "deepseek" | "openai" | "lmstudio" | "ollama";

interface ProviderForm {
  base_url: string;
  model: string;
  api_key: string;
}

const PROVIDER_LABELS: Record<ProviderId, string> = {
  deepseek: "DeepSeek V4 Flash",
  openai: "OpenAI",
  lmstudio: "LM Studio",
  ollama: "Ollama",
};

const CLOUD: ProviderId[] = ["deepseek", "openai"];

function emptyProviderForm(): ProviderForm {
  return { base_url: "", model: "", api_key: "" };
}

function SecretInput({
  value,
  onChange,
  placeholder,
  inputClassName = "w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 pr-10 text-sm font-mono",
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  inputClassName?: string;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="relative mt-1">
      <input
        type={visible ? "text" : "password"}
        className={inputClassName}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        autoComplete="off"
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-zinc-500 hover:text-zinc-300 rounded"
        aria-label={visible ? "Hide secret" : "Show secret"}
        tabIndex={-1}
      >
        {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
      </button>
    </div>
  );
}

export default function SettingsPage() {
  const qc = useQueryClient();
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  });

  const [defaultProvider, setDefaultProvider] = useState("deepseek");
  const [providers, setProviders] = useState<Record<ProviderId, ProviderForm>>({
    deepseek: emptyProviderForm(),
    openai: emptyProviderForm(),
    lmstudio: emptyProviderForm(),
    ollama: emptyProviderForm(),
  });
  const [discoveries, setDiscoveries] = useState<LlmDiscovery[]>([]);
  const [pexelsKey, setPexelsKey] = useState("");
  const [stockProvider, setStockProvider] = useState("pexels");
  const [cogvideoUrl, setCogvideoUrl] = useState("http://localhost:8188");
  const [googleApiKey, setGoogleApiKey] = useState("");
  const [googleProject, setGoogleProject] = useState("");
  const [googleMcpUrl, setGoogleMcpUrl] = useState("http://127.0.0.1:11014");
  const [jellyfinUrl, setJellyfinUrl] = useState("http://127.0.0.1:8096");
  const [jellyfinKey, setJellyfinKey] = useState("");
  const [plexUrl, setPlexUrl] = useState("http://127.0.0.1:32400");
  const [plexToken, setPlexToken] = useState("");
  const [stockProbe, setStockProbe] = useState("");
  const [edgeVoice, setEdgeVoice] = useState("en-US-AriaNeural");
  const [scanMessage, setScanMessage] = useState("");

  useEffect(() => {
    if (!data) return;
    setDefaultProvider(data.settings.videogen_llm_provider);
    setStockProvider(data.settings.videogen_stock_provider || "pexels");
    setCogvideoUrl(data.settings.cogvideo_url || "http://localhost:8188");
    setGoogleProject(data.settings.google_cloud_project || "");
    setGoogleMcpUrl(data.settings.google_ai_mcp_url || "http://127.0.0.1:11014");
    setJellyfinUrl(data.settings.jellyfin_server_url || "http://127.0.0.1:8096");
    setJellyfinKey(data.settings.jellyfin_api_key_set ? SECRET_MASK : "");
    setPlexUrl(data.settings.plex_url || "http://127.0.0.1:32400");
    setPlexToken(data.settings.plex_token_set ? SECRET_MASK : "");
    setGoogleApiKey(data.settings.google_api_key_set ? SECRET_MASK : "");
    setEdgeVoice(data.settings.edge_tts_voice);
    setPexelsKey(data.settings.pexels_api_key_set ? SECRET_MASK : "");
    setDiscoveries(data.models);

    const next: Record<ProviderId, ProviderForm> = {
      deepseek: emptyProviderForm(),
      openai: emptyProviderForm(),
      lmstudio: emptyProviderForm(),
      ollama: emptyProviderForm(),
    };
    for (const p of data.settings.llm_providers) {
      const id = p.id as ProviderId;
      next[id] = {
        base_url: p.base_url,
        model: p.model,
        api_key: p.api_key_set && CLOUD.includes(id) ? SECRET_MASK : "",
      };
    }
    setProviders(next);
  }, [data]);

  const discoveryMap = useMemo(() => {
    const m = new Map<string, LlmDiscovery>();
    for (const d of discoveries) m.set(d.provider, d);
    return m;
  }, [discoveries]);

  const scanMutation = useMutation({
    mutationFn: () => refreshModels() as Promise<LlmDiscovery[]>,
    onSuccess: (found) => {
      setDiscoveries(found);
      const ready = found.filter((d) => d.available).map((d) => d.provider);
      setScanMessage(
        ready.length
          ? `Found models for: ${ready.join(", ")}`
          : "No local servers reachable; cloud needs API keys saved first."
      );
      setProviders((prev) => {
        const copy = { ...prev };
        for (const d of found) {
          const id = d.provider as ProviderId;
          if (!copy[id].model && d.selected_model) {
            copy[id] = { ...copy[id], model: d.selected_model };
          }
        }
        return copy;
      });
    },
    onError: (e: Error) => setScanMessage(e.message),
  });

  const stockProbeMutation = useMutation({
    mutationFn: refreshStockStatus,
    onSuccess: (res) => {
      const s = res.stock;
      const parts: string[] = [];
      if (s.pexels_ready) parts.push("Pexels OK");
      if (s.cogvideo_ready) parts.push(`LocalGen @ ${s.cogvideo_url}`);
      if (s.veo_ready) parts.push("Veo ready");
      if (s.omni_ready) parts.push("Omni ready");
      if (s.jellyfin_ready) parts.push("Jellyfin ready");
      if (s.plex_ready) parts.push("Plex ready");
      if (!parts.length) {
        parts.push(s.cogvideo_error || s.hint);
      }
      setStockProbe(parts.join(" · "));
    },
    onError: (e: Error) => setStockProbe(e.message),
  });

  const saveMutation = useMutation({
    mutationFn: (payload: SettingsSavePayload) => saveSettings(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["settings"] });
      qc.invalidateQueries({ queryKey: ["status"] });
      refetch();
    },
  });

  function modelOptions(id: ProviderId): string[] {
    const discovered = discoveryMap.get(id)?.models ?? [];
    const current = providers[id].model;
    if (current && !discovered.includes(current)) return [current, ...discovered];
    return discovered.length ? discovered : current ? [current] : [];
  }

  function updateProvider(id: ProviderId, patch: Partial<ProviderForm>) {
    setProviders((prev) => ({ ...prev, [id]: { ...prev[id], ...patch } }));
  }

  function buildPayload(): SettingsSavePayload {
    const payload: SettingsSavePayload = {
      videogen_llm_provider: defaultProvider,
      videogen_tts_provider: "edge-tts",
      videogen_stock_provider: stockProvider,
      cogvideo_url: cogvideoUrl,
      google_cloud_project: googleProject,
      google_ai_mcp_url: googleMcpUrl,
      edge_tts_voice: edgeVoice,
      deepseek_base_url: providers.deepseek.base_url,
      deepseek_model: providers.deepseek.model,
      openai_base_url: providers.openai.base_url,
      openai_model: providers.openai.model,
      lmstudio_base_url: providers.lmstudio.base_url,
      lmstudio_model: providers.lmstudio.model,
      ollama_base_url: providers.ollama.base_url,
      ollama_model: providers.ollama.model,
    };

    if (providers.deepseek.api_key && providers.deepseek.api_key !== SECRET_MASK) {
      payload.deepseek_api_key = providers.deepseek.api_key;
    }
    if (providers.openai.api_key && providers.openai.api_key !== SECRET_MASK) {
      payload.openai_api_key = providers.openai.api_key;
    }
    if (pexelsKey && pexelsKey !== SECRET_MASK) {
      payload.pexels_api_key = pexelsKey;
    }
    if (googleApiKey && googleApiKey !== SECRET_MASK) {
      payload.google_api_key = googleApiKey;
    }
    if (jellyfinUrl) payload.jellyfin_server_url = jellyfinUrl;
    if (jellyfinKey && jellyfinKey !== SECRET_MASK) payload.jellyfin_api_key = jellyfinKey;
    if (plexUrl) payload.plex_url = plexUrl;
    if (plexToken && plexToken !== SECRET_MASK) payload.plex_token = plexToken;
    return payload;
  }

  if (isLoading && !data) {
    return <p className="text-sm text-zinc-500">Loading settings…</p>;
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-sm text-zinc-500 mt-1">
            LLM providers, models, and API keys · saved to{" "}
            <code className="text-xs text-zinc-400">{data?.settings.env_path ?? ".env"}</code>
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={scanMutation.isPending}
            onClick={() => scanMutation.mutate()}
            className="px-3 py-2 text-sm rounded-md border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40"
          >
            {scanMutation.isPending ? "Scanning…" : "Scan models"}
          </button>
          <button
            type="button"
            disabled={saveMutation.isPending}
            onClick={() => saveMutation.mutate(buildPayload())}
            className="px-4 py-2 text-sm rounded-md bg-blue-600 hover:bg-blue-500 disabled:opacity-40 font-medium"
          >
            {saveMutation.isPending ? "Saving…" : "Save config"}
          </button>
        </div>
      </div>

      {scanMessage && <p className="text-sm text-zinc-400">{scanMessage}</p>}
      {saveMutation.isSuccess && (
        <p className="text-sm text-emerald-400">Settings saved. Restart not required — backend reloads .env.</p>
      )}
      {saveMutation.isError && (
        <p className="text-sm text-red-400">{(saveMutation.error as Error).message}</p>
      )}

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-4">
        <h2 className="text-sm font-semibold text-zinc-300">Default script writer</h2>
        <label className="block text-sm max-w-xs">
          <span className="text-zinc-500">Provider used on Generate (topic modes)</span>
          <select
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
            value={defaultProvider}
            onChange={(e) => setDefaultProvider(e.target.value)}
          >
            {(Object.keys(PROVIDER_LABELS) as ProviderId[]).map((id) => (
              <option key={id} value={id}>
                {PROVIDER_LABELS[id]}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-zinc-300">LLM providers</h2>
        {(Object.keys(PROVIDER_LABELS) as ProviderId[]).map((id) => {
          const meta = data?.settings.llm_providers.find((p) => p.id === id);
          const discovery = discoveryMap.get(id);
          const options = modelOptions(id);
          const isCloud = CLOUD.includes(id);

          return (
            <div key={id} className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4 space-y-3">
              <div className="flex items-center justify-between gap-2">
                <p className="font-medium text-sm">{PROVIDER_LABELS[id]}</p>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    meta?.ready || discovery?.available
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : "bg-amber-950 text-amber-400 border border-amber-800"
                  }`}
                >
                  {meta?.ready || discovery?.available ? "Ready" : "Unavailable"}
                </span>
              </div>

              {discovery?.error && !discovery.available && (
                <p className="text-xs text-amber-300/90">{discovery.error}</p>
              )}

              <div className="grid md:grid-cols-2 gap-3">
                <label className="block text-sm">
                  <span className="text-zinc-500">Base URL</span>
                  <input
                    className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                    value={providers[id].base_url}
                    onChange={(e) => updateProvider(id, { base_url: e.target.value })}
                  />
                </label>

                <label className="block text-sm">
                  <span className="text-zinc-500">Model</span>
                  <select
                    className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                    value={providers[id].model}
                    onChange={(e) => updateProvider(id, { model: e.target.value })}
                  >
                    {options.length === 0 && <option value="">Scan models or type below</option>}
                    {options.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                  <input
                    className="mt-2 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-xs font-mono"
                    placeholder="Or enter model id manually"
                    value={providers[id].model}
                    onChange={(e) => updateProvider(id, { model: e.target.value })}
                  />
                </label>
              </div>

              {isCloud && (
                <label className="block text-sm">
                  <span className="text-zinc-500">
                    API key {meta?.api_key_hint ? `(current ${meta.api_key_hint})` : ""}
                  </span>
                  <SecretInput
                    placeholder={meta?.api_key_set ? SECRET_MASK : "sk-…"}
                    value={providers[id].api_key}
                    onChange={(v) => updateProvider(id, { api_key: v })}
                  />
                  <span className="text-[10px] text-zinc-600 mt-1 block">
                    Leave as {SECRET_MASK} to keep existing key
                  </span>
                </label>
              )}
            </div>
          );
        })}
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-zinc-300">Footage source</h2>
          <span
            className={`text-xs px-2 py-0.5 rounded-full ${
              data?.settings.stock_ready_for_renders
                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                : "bg-amber-950 text-amber-400 border border-amber-800"
            }`}
          >
            {data?.settings.stock_ready_for_renders ? "Ready" : "Not ready"}
          </span>
        </div>
        <p className="text-xs text-zinc-500">{data?.settings.stock_hint}</p>

        <label className="block text-sm max-w-xs">
          <span className="text-zinc-500">Provider</span>
          <select
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
            value={stockProvider}
            onChange={(e) => setStockProvider(e.target.value)}
          >
            <option value="pexels">Pexels (cloud stock)</option>
            <option value="veo">Google Veo 3.x (cloud AI)</option>
            <option value="omni">Gemini Omni Flash (cloud AI)</option>
            <option value="localgen">LocalGen — Wan 2.2 (2026)</option>
            <option value="cogvideo">LocalGen (legacy id: cogvideo)</option>
            <option value="jellyfin">Jellyfin — your library</option>
            <option value="plex">Plex — your library</option>
          </select>
        </label>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            disabled={stockProbeMutation.isPending}
            onClick={() => stockProbeMutation.mutate()}
            className="px-3 py-1.5 text-xs rounded-md border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40"
          >
            {stockProbeMutation.isPending ? "Probing…" : "Test footage providers"}
          </button>
          {stockProbe && <span className="text-xs text-zinc-500">{stockProbe}</span>}
        </div>

        {stockProvider === "pexels" && (
          <label className="block text-sm">
            <span className="text-zinc-500">
              Pexels API key{" "}
              {data?.settings.pexels_api_key_hint ? `(current ${data.settings.pexels_api_key_hint})` : ""}
            </span>
            <SecretInput
              inputClassName="w-full max-w-lg rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 pr-10 text-sm font-mono"
              value={pexelsKey}
              onChange={setPexelsKey}
              placeholder={data?.settings.pexels_api_key_set ? SECRET_MASK : "Pexels key"}
            />
          </label>
        )}

        {(stockProvider === "veo" || stockProvider === "omni") && (
          <div className="space-y-3 rounded-md border border-zinc-800 bg-zinc-950/50 p-4">
            <p className="text-xs text-zinc-400">
              {stockProvider === "veo" ? (
                <>
                  <strong className="text-zinc-200">Google Veo 3.x</strong> — cinematic AI clips (~5–8 s).
                  Recommended: run fleet <code className="text-zinc-500">google-ai-mcp</code> on :11014 and
                  bridge below.
                </>
              ) : (
                <>
                  <strong className="text-zinc-200">Gemini Omni Flash</strong> — multimodal text→video (~10 s).
                </>
              )}
            </p>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">google-ai-mcp URL (bridge)</span>
              <input
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                value={googleMcpUrl}
                onChange={(e) => setGoogleMcpUrl(e.target.value)}
                placeholder="http://127.0.0.1:11014"
              />
            </label>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">
                Google API key (direct fallback){" "}
                {data?.settings.google_api_key_hint ? `(current ${data.settings.google_api_key_hint})` : ""}
              </span>
              <SecretInput
                inputClassName="w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 pr-10 text-sm font-mono"
                value={googleApiKey}
                onChange={setGoogleApiKey}
                placeholder={data?.settings.google_api_key_set ? SECRET_MASK : "AI Studio / Gemini key"}
              />
            </label>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">GCP project (Veo / Vertex direct)</span>
              <input
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                value={googleProject}
                onChange={(e) => setGoogleProject(e.target.value)}
                placeholder="my-gcp-project"
              />
            </label>
            <p className="text-xs text-zinc-600">
              Bridge: start google-ai-mcp · Direct:{" "}
              <code className="text-zinc-400">pip install -e &quot;.[google]&quot;</code>
            </p>
            <span
              className={`text-xs block ${
                stockProvider === "veo"
                  ? data?.settings.veo_ready
                    ? "text-emerald-400"
                    : "text-amber-400"
                  : data?.settings.omni_ready
                    ? "text-emerald-400"
                    : "text-amber-400"
              }`}
            >
              {stockProvider === "veo"
                ? data?.settings.veo_ready
                  ? "Veo layer ready"
                  : "Veo not ready — check bridge or credentials"
                : data?.settings.omni_ready
                  ? "Omni layer ready"
                  : "Omni not ready — check bridge or credentials"}
            </span>
          </div>
        )}

        {(stockProvider === "localgen" || stockProvider === "cogvideo") && (
          <div className="space-y-3 rounded-md border border-zinc-800 bg-zinc-950/50 p-4">
            <p className="text-xs text-zinc-400">
              2026 tier: <strong className="text-zinc-200">Wan 2.2</strong> (14B default on 4090, ~4–5 min/clip).
              Fast mode: set <code className="text-zinc-500">LOCALGEN_BACKEND=wan22-5b</code> before starting sidecar.
            </p>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">Sidecar URL</span>
              <input
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                value={cogvideoUrl}
                onChange={(e) => setCogvideoUrl(e.target.value)}
                placeholder="http://localhost:8188"
              />
            </label>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                disabled={stockProbeMutation.isPending}
                onClick={() => stockProbeMutation.mutate()}
                className="px-3 py-1.5 text-xs rounded-md border border-zinc-700 hover:bg-zinc-800 disabled:opacity-40"
              >
                {stockProbeMutation.isPending ? "Probing…" : "Test LocalGen"}
              </button>
              <span
                className={`text-xs ${
                  data?.settings.cogvideo_ready ? "text-emerald-400" : "text-amber-400"
                }`}
              >
                {data?.settings.cogvideo_ready ? "Server reachable" : "Server offline"}
              </span>
            </div>
            {data?.settings.cogvideo_error && !data.settings.cogvideo_ready && (
              <p className="text-xs text-amber-300/90">{data.settings.cogvideo_error}</p>
            )}
            <p className="text-xs text-zinc-600">
              Start: <code className="text-zinc-400">start-localgen.bat</code> · Install:{" "}
              <code className="text-zinc-400">py -m pip install -e &quot;.[localgen]&quot;</code>
            </p>
            {stockProbe && <p className="text-xs text-zinc-500">{stockProbe}</p>}
          </div>
        )}

        {stockProvider === "jellyfin" && (
          <div className="space-y-3 rounded-md border border-zinc-800 bg-zinc-950/50 p-4">
            <p className="text-xs text-zinc-400">
              Search your Jellyfin libraries (vacation, dog cam, home videos) and ffmpeg-cut ~5 s B-roll
              segments. Same credentials as fleet <code className="text-zinc-500">jellyfin-mcp</code>.
            </p>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">Jellyfin server URL</span>
              <input
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                value={jellyfinUrl}
                onChange={(e) => setJellyfinUrl(e.target.value)}
                placeholder="http://127.0.0.1:8096"
              />
            </label>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">
                API key{" "}
                {data?.settings.jellyfin_api_key_hint
                  ? `(current ${data.settings.jellyfin_api_key_hint})`
                  : ""}
              </span>
              <SecretInput
                value={jellyfinKey}
                onChange={setJellyfinKey}
                placeholder={data?.settings.jellyfin_api_key_set ? SECRET_MASK : "Jellyfin API key"}
              />
            </label>
          </div>
        )}

        {stockProvider === "plex" && (
          <div className="space-y-3 rounded-md border border-zinc-800 bg-zinc-950/50 p-4">
            <p className="text-xs text-zinc-400">
              Search Plex and cut clips from your own libraries. Same <code className="text-zinc-500">PLEX_URL</code>{" "}
              + <code className="text-zinc-500">PLEX_TOKEN</code> as <code className="text-zinc-500">plex-mcp</code>.
            </p>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">Plex server URL</span>
              <input
                className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
                value={plexUrl}
                onChange={(e) => setPlexUrl(e.target.value)}
                placeholder="http://127.0.0.1:32400"
              />
            </label>
            <label className="block text-sm max-w-lg">
              <span className="text-zinc-500">
                Token{" "}
                {data?.settings.plex_token_hint ? `(current ${data.settings.plex_token_hint})` : ""}
              </span>
              <SecretInput
                value={plexToken}
                onChange={setPlexToken}
                placeholder={data?.settings.plex_token_set ? SECRET_MASK : "X-Plex-Token"}
              />
            </label>
          </div>
        )}
      </section>

      <section className="rounded-lg border border-zinc-800 bg-zinc-900/80 p-5 space-y-3">
        <h2 className="text-sm font-semibold text-zinc-300">Voice (edge-tts)</h2>
        <label className="block text-sm max-w-lg">
          <span className="text-zinc-500">Voice id</span>
          <input
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm font-mono"
            value={edgeVoice}
            onChange={(e) => setEdgeVoice(e.target.value)}
          />
        </label>
      </section>

      {isFetching && <p className="text-xs text-zinc-600">Refreshing…</p>}
    </div>
  );
}
