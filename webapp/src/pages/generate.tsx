import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { generateVideo } from "@/lib/api";
import { useJobsStore } from "@/store/jobs";

export default function Generate() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const setActiveJobId = useJobsStore((s) => s.setActiveJobId);
  const [topic, setTopic] = useState("");
  const [aspect, setAspect] = useState("9:16");
  const [paragraphs, setParagraphs] = useState(3);

  const mutation = useMutation({
    mutationFn: () =>
      generateVideo({
        topic,
        aspect,
        paragraph_count: paragraphs,
        clip_duration: 5,
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
        <h1 className="text-2xl font-bold">Short video</h1>
        <p className="text-sm text-zinc-500 mt-1">30–60s · TikTok / Reels / Shorts · default 9:16</p>
      </div>

      <form
        className="space-y-4 rounded-lg border border-zinc-800 bg-zinc-900/80 p-5"
        onSubmit={(e) => {
          e.preventDefault();
          mutation.mutate();
        }}
      >
        <label className="block text-sm">
          <span className="text-zinc-400">Topic</span>
          <input
            className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm focus:border-blue-500 outline-none"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Why cats are amazing pets"
            required
          />
        </label>

        <div className="grid grid-cols-2 gap-3">
          <label className="block text-sm">
            <span className="text-zinc-400">Aspect</span>
            <select
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={aspect}
              onChange={(e) => setAspect(e.target.value)}
            >
              <option value="9:16">9:16 (vertical)</option>
              <option value="16:9">16:9 (landscape)</option>
              <option value="1:1">1:1</option>
            </select>
          </label>
          <label className="block text-sm">
            <span className="text-zinc-400">Segments</span>
            <input
              type="number"
              min={1}
              max={10}
              className="mt-1 w-full rounded-md bg-zinc-950 border border-zinc-700 px-3 py-2 text-sm"
              value={paragraphs}
              onChange={(e) => setParagraphs(Number(e.target.value))}
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={mutation.isPending || !topic.trim()}
          className="w-full py-2.5 rounded-md bg-blue-600 font-medium text-sm hover:bg-blue-500 disabled:opacity-40"
        >
          {mutation.isPending ? "Starting…" : "Generate"}
        </button>
        {mutation.isError && (
          <p className="text-sm text-red-400">{(mutation.error as Error).message}</p>
        )}
      </form>
    </div>
  );
}
