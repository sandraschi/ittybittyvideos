import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  Sparkles,
  Video,
  Layers,
  Cpu,
  CheckCircle2,
  AlertCircle,
  Download,
  RefreshCw,
  Film
} from "lucide-react";

interface LocalGenHealth {
  status: string;
  service: string;
  tier: string;
  backend: string;
  label: string;
  model_id: string;
  model_loaded: boolean;
  cuda_available: boolean;
  device: string;
  memory_mode?: string;
  deps_installed: boolean;
  backends_available: string[];
  hint: string;
}

const BACKEND_PRESETS = [
  {
    id: "longcat-video-13b",
    name: "LongCat-Video 13.6B",
    tag: "DiT Continuation",
    badge: "2026 SOTA",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    desc: "13.6B Dense DiT pretrained on Video Continuation. 720p @ 30 FPS.",
    vram: "16–24 GB VRAM",
    supportsExtend: true,
  },
  {
    id: "wan22-14b",
    name: "Wan 2.2 T2V 14B",
    tag: "Text-to-Video",
    badge: "2026 Tier",
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    desc: "High-fidelity text-to-video generation by Wan-AI. 16 FPS.",
    vram: "14–24 GB VRAM",
    supportsExtend: false,
  },
  {
    id: "wan22-5b",
    name: "Wan 2.2 TI2V 5B",
    tag: "Fast TI2V",
    badge: "2026 Fast",
    badgeColor: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    desc: "Lightweight 5B text & image-to-video model for rapid drafting. 24 FPS.",
    vram: "8–12 GB VRAM",
    supportsExtend: false,
  },
  {
    id: "cogvideo-2b",
    name: "CogVideoX 2B",
    tag: "Legacy",
    badge: "Legacy",
    badgeColor: "bg-zinc-500/20 text-zinc-400 border-zinc-500/30",
    desc: "Legacy 2B model by THUDM. 8 FPS output.",
    vram: "6–8 GB VRAM",
    supportsExtend: false,
  },
];

export default function LocalGenStudio() {
  const [activeTab, setActiveTab] = useState<"generate" | "extend">("generate");
  const [selectedBackend, setSelectedBackend] = useState("longcat-video-13b");
  const [prompt, setPrompt] = useState("A majestic lion walking through a sunlit tropical rainforest, 8k resolution, cinematic lighting");
  const [extendPrompt, setExtendPrompt] = useState("The camera pans upwards toward the canopy as sunlight breaks through the leaves");
  const [aspect, setAspect] = useState("16:9");
  const [numFrames, setNumFrames] = useState(81);
  const [guidanceScale, setGuidanceScale] = useState(4.5);
  const [generatedVideoUrl, setGeneratedVideoUrl] = useState<string | null>(null);

  // Fetch localgen health status from sidecar
  const { data: health, refetch: refetchHealth, isFetching } = useQuery<LocalGenHealth>({
    queryKey: ["localgen-health"],
    queryFn: async () => {
      const res = await fetch("http://localhost:8188/api/health");
      if (!res.ok) throw new Error("LocalGen sidecar offline");
      return res.json();
    },
    refetchInterval: 10000,
    retry: 1,
  });

  const generateMutation = useMutation({
    mutationFn: async () => {
      const endpoint = activeTab === "extend" ? "/api/extend" : "/api/generate";
      const payload = {
        prompt: activeTab === "extend" ? extendPrompt : prompt,
        aspect,
        num_frames: numFrames,
        guidance_scale: guidanceScale,
      };

      const res = await fetch(`http://localhost:8188${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: "Generation failed" }));
        throw new Error(errorData.detail || "Generation failed");
      }

      const blob = await res.blob();
      return URL.createObjectURL(blob);
    },
    onSuccess: (url) => {
      setGeneratedVideoUrl(url);
    },
  });

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight">LocalGen Studio</h1>
            <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
              LongCat 13.6B & Wan 2.2
            </span>
          </div>
          <p className="text-sm text-zinc-400 mt-1">
            Local AI video synthesis sidecar engine. Generate and extend high-fidelity videos on GPU.
          </p>
        </div>

        <button
          onClick={() => refetchHealth()}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-md transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? "animate-spin" : ""}`} />
          Check Health
        </button>
      </div>

      {/* Sidecar Status Banner */}
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/60 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${health?.status === "ok" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
              {health?.status === "ok" ? <CheckCircle2 className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-zinc-200">
                  {health ? `Sidecar Status: ${health.label}` : "LocalGen Sidecar (:8188)"}
                </span>
                {health?.cuda_available && (
                  <span className="px-2 py-0.5 text-[10px] font-mono bg-emerald-950 text-emerald-400 rounded border border-emerald-800">
                    CUDA Active ({health.device})
                  </span>
                )}
              </div>
              <p className="text-xs text-zinc-400 mt-0.5">
                {health?.hint || "Make sure sidecar is running via `python -m videogen_mcp.localgen_server`"}
              </p>
            </div>
          </div>

          <div className="text-right text-xs font-mono text-zinc-500">
            <div>Engine: {health?.backend || selectedBackend}</div>
            <div>Loaded: {health?.model_loaded ? "Yes" : "Lazy (on first frame)"}</div>
          </div>
        </div>
      </div>

      {/* Backend Selection Cards */}
      <div>
        <label className="text-xs font-semibold text-zinc-400 tracking-wide uppercase mb-3 block">
          Select AI Video Engine
        </label>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {BACKEND_PRESETS.map((b) => (
            <div
              key={b.id}
              onClick={() => setSelectedBackend(b.id)}
              className={`cursor-pointer rounded-lg border p-3.5 transition-all ${
                selectedBackend === b.id
                  ? "border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/5"
                  : "border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 hover:bg-zinc-900"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${b.badgeColor}`}>
                  {b.badge}
                </span>
                <span className="text-[10px] font-mono text-zinc-500">{b.vram}</span>
              </div>
              <h3 className="text-sm font-bold text-zinc-200">{b.name}</h3>
              <p className="text-xs text-zinc-400 mt-1 line-clamp-2">{b.desc}</p>
              {b.supportsExtend && (
                <div className="mt-2.5 flex items-center gap-1 text-[10px] font-medium text-purple-400">
                  <Layers className="w-3 h-3" />
                  Supports Video Extension
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Studio Control Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Generation Controls */}
        <div className="lg:col-span-7 space-y-4 rounded-xl border border-zinc-800 bg-zinc-900/70 p-5">
          {/* Mode Switch Tabs */}
          <div className="flex rounded-lg bg-zinc-950 p-1 border border-zinc-800">
            <button
              onClick={() => setActiveTab("generate")}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-colors ${
                activeTab === "generate" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Film className="w-3.5 h-3.5" />
              Text-to-Video (T2V)
            </button>
            <button
              onClick={() => setActiveTab("extend")}
              className={`flex-1 flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-colors ${
                activeTab === "extend" ? "bg-purple-900/60 text-purple-200 border border-purple-500/30" : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Video Continuation (LongCat)
            </button>
          </div>

          {/* Prompt Section */}
          {activeTab === "generate" ? (
            <div>
              <label className="text-xs font-medium text-zinc-300 block mb-1.5">
                Video Generation Prompt
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={4}
                className="w-full rounded-lg bg-zinc-950 border border-zinc-800 p-3 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-blue-500 transition-colors"
                placeholder="Describe your scene in detail..."
              />
            </div>
          ) : (
            <div>
              <label className="text-xs font-medium text-purple-300 block mb-1.5">
                Continuation Prompt (Extend Clip)
              </label>
              <textarea
                value={extendPrompt}
                onChange={(e) => setExtendPrompt(e.target.value)}
                rows={4}
                className="w-full rounded-lg bg-zinc-950 border border-purple-900/50 p-3 text-sm text-purple-100 placeholder-zinc-600 focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="Describe what happens next in the extended video..."
              />
            </div>
          )}

          {/* Aspect Ratio Picker */}
          <div>
            <label className="text-xs font-medium text-zinc-400 block mb-1.5">Aspect Ratio</label>
            <div className="flex gap-2">
              {["16:9", "9:16", "1:1"].map((asp) => (
                <button
                  key={asp}
                  onClick={() => setAspect(asp)}
                  className={`px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                    aspect === asp
                      ? "bg-blue-600 text-white shadow"
                      : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
                  }`}
                >
                  {asp}
                </button>
              ))}
            </div>
          </div>

          {/* Sliders: Frames & Guidance */}
          <div className="grid grid-cols-2 gap-4 pt-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-400">Frames</span>
                <span className="font-mono font-semibold text-zinc-200">{numFrames} frames</span>
              </div>
              <input
                type="range"
                min={16}
                max={121}
                step={8}
                value={numFrames}
                onChange={(e) => setNumFrames(Number(e.target.value))}
                className="w-full accent-blue-500 bg-zinc-800"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-zinc-400 font-medium">Guidance Scale</span>
                <span className="font-mono font-semibold text-zinc-200">{guidanceScale.toFixed(1)}</span>
              </div>
              <input
                type="range"
                min={1.0}
                max={15.0}
                step={0.5}
                value={guidanceScale}
                onChange={(e) => setGuidanceScale(Number(e.target.value))}
                className="w-full accent-blue-500 bg-zinc-800"
              />
            </div>
          </div>

          {/* Action Button */}
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className={`w-full py-3 rounded-lg font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
              activeTab === "extend"
                ? "bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-600/20"
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {generateMutation.isPending ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Synthesizing Video Frames...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                {activeTab === "extend" ? "Extend Video with LongCat-Video" : "Generate Video Clip"}
              </>
            )}
          </button>

          {generateMutation.isError && (
            <div className="p-3 rounded-lg bg-red-950/50 border border-red-800 text-red-300 text-xs">
              {(generateMutation.error as Error).message}
            </div>
          )}
        </div>

        {/* Right Column: Output Preview & Tech Info */}
        <div className="lg:col-span-5 space-y-4">
          {/* Video Preview Box */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 aspect-video flex flex-col items-center justify-center relative overflow-hidden">
            {generatedVideoUrl ? (
              <video
                src={generatedVideoUrl}
                controls
                autoPlay
                loop
                className="w-full h-full object-contain rounded-lg"
              />
            ) : (
              <div className="text-center p-6 space-y-2">
                <Video className="w-10 h-10 text-zinc-700 mx-auto" />
                <p className="text-xs text-zinc-500">
                  Synthesized MP4 video will preview here
                </p>
              </div>
            )}
          </div>

          {/* Video Actions */}
          {generatedVideoUrl && (
            <div className="flex gap-2">
              <a
                href={generatedVideoUrl}
                download="generated-clip.mp4"
                className="flex-1 py-2 px-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Download MP4
              </a>
            </div>
          )}

          {/* Model Tech Card */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 space-y-2.5">
            <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-blue-400" />
              Engine Architecture
            </h4>
            <div className="space-y-1.5 text-xs text-zinc-400">
              <div className="flex justify-between">
                <span>Model Architecture</span>
                <span className="font-mono text-zinc-200">13.6B Dense DiT</span>
              </div>
              <div className="flex justify-between">
                <span>Native Resolution</span>
                <span className="font-mono text-zinc-200">720p @ 30 FPS</span>
              </div>
              <div className="flex justify-between">
                <span>Continuation Support</span>
                <span className="font-mono text-purple-400">Pretrained Native</span>
              </div>
              <div className="flex justify-between">
                <span>Memory Offloading</span>
                <span className="font-mono text-emerald-400">CPU-Offload Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
