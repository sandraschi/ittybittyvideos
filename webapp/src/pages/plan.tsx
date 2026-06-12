import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { planRender, planVideo } from "@/lib/api";
import type { PromptNavState } from "@/lib/prompt-library";
import { useJobsStore } from "@/store/jobs";

export default function Plan() {
  const navigate = useNavigate();
  const location = useLocation();
  const qc = useQueryClient();
  const setActiveJobId = useJobsStore((s) => s.setActiveJobId);
  const [topic, setTopic] = useState("");
  const [videoType, setVideoType] = useState("explainer");
  const [duration, setDuration] = useState(300);
  const [preview, setPreview] = useState<string>("");
  const [structureNote, setStructureNote] = useState<string | null>(null);

  useEffect(() => {
    const s = location.state as PromptNavState | null;
    if (!s?.topic) return;
    setTopic(s.topic);
    if (s.videoType) setVideoType(s.videoType);
    const notes = [s.structure, s.styleNotes].filter(Boolean).join(" · ");
    setStructureNote(notes || null);
    navigate(location.pathname, { replace: true, state: null });
  }, [location.pathname, location.state, navigate]);

  const previewMut = useMutation({
    mutationFn: () =>
      planVideo({
        topic,
        video_type: videoType,
        target_duration: duration,
        chapters: 4,
      }),
    onSuccess: (data) => {
      const b = data.storyboard;
      setPreview(
        `${b.title}\n${b.total_scenes} scenes · ${Math.round(b.planned_duration)}s planned · ${b.chapters.length} chapters`,
      );
    },
  });

  const renderMut = useMutation({
    mutationFn: () =>
      planRender({
        topic,
        video_type: videoType,
        target_duration: duration,
        aspect: "16:9",
        chapters: 4,
      }),
    onSuccess: (data) => {
      setActiveJobId(data.job_id);
      qc.invalidateQueries({ queryKey: ["jobs"] });
      navigate(`/jobs?highlight=${data.job_id}`);
    },
  });

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Mid-length video</h1>
        <p className="text-sm text-zinc-500 mt-1">
          3–15 min · chaptered storyboard + videographer rules ·{" "}
          <Link to="/prompts" className="text-blue-500 hover:underline">
            Prompt library
          </Link>
        </p>
        {structureNote && (
          <p className="text-xs text-violet-400/90 mt-1">
            From library (R10 structure not sent to API yet): {structureNote}
          </p>
        )}
      </div>

      <div className="space-y-4 rounded-lg border border-zinc-800 bg-zinc-900/80 p-5">
        <label className="block text-sm">
          <span className="text-zinc-400">Topic</span>
          <input
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="How quantum computing works"
          />
        </label>

        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm">
            <span className="text-zinc-400">Type</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={videoType}
              onChange={(e) => setVideoType(e.target.value)}
            >
              <option value="explainer">Explainer</option>
              <option value="tutorial">Tutorial</option>
              <option value="demo">Demo</option>
              <option value="documentary">Documentary</option>
              <option value="showcase">Showcase</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-zinc-400">Target (seconds)</span>
            <input
              type="number"
              min={30}
              max={900}
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </label>
        </div>

        {preview && (
          <pre className="text-xs bg-zinc-950 border border-zinc-800 rounded p-3 text-emerald-400 whitespace-pre-wrap">
            {preview}
          </pre>
        )}

        <div className="flex gap-2">
          <button
            type="button"
            disabled={!topic.trim() || previewMut.isPending}
            onClick={() => previewMut.mutate()}
            className="flex-1 py-2 rounded-md border border-zinc-700 text-sm hover:bg-zinc-800 disabled:opacity-40"
          >
            Preview plan
          </button>
          <button
            type="button"
            disabled={!topic.trim() || renderMut.isPending}
            onClick={() => renderMut.mutate()}
            className="flex-1 py-2 rounded-md bg-blue-600 text-sm font-medium hover:bg-blue-500 disabled:opacity-40"
          >
            Plan & render
          </button>
        </div>
      </div>
    </div>
  );
}
