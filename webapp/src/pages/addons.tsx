import { useEffect, useState } from "react";

interface Addon {
  id: string;
  name: string;
  description: string;
  size_mb: number;
  features: string[];
  installed: boolean;
}

export default function AddonsPage() {
  const [addons, setAddons] = useState<Addon[]>([]);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState<string | null>(null);

  const fetchAddons = async () => {
    try {
      const res = await fetch("/api/v1/addons");
      const data = await res.json();
      if (data.success) setAddons(data.addons);
    } catch (e) {
      console.error("Failed to fetch addons", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAddons(); }, []);

  const installAll = async () => {
    setInstalling("all");
    try {
      await fetch("/api/v1/addons/install-all", { method: "POST" });
      await fetchAddons();
    } finally {
      setInstalling(null);
    }
  };

  const installOne = async (id: string) => {
    setInstalling(id);
    try {
      await fetch(`/api/v1/addons/${id}/install`, { method: "POST" });
      await fetchAddons();
    } finally {
      setInstalling(null);
    }
  };

  const uninstallOne = async (id: string) => {
    setInstalling(id);
    try {
      await fetch(`/api/v1/addons/${id}`, { method: "DELETE" });
      await fetchAddons();
    } finally {
      setInstalling(null);
    }
  };

  const totalSize = addons.reduce((sum, a) => sum + a.size_mb, 0);
  const installedCount = addons.filter(a => a.installed).length;
  const allInstalled = installedCount === addons.length;

  if (loading) return <div className="p-6 text-zinc-400">Loading addons...</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Addons</h1>
        <p className="text-zinc-400 text-sm mt-1">
          The core app is lean ({"\u003C"}60 MB). Heavy AI modules download on demand.
        </p>
      </div>

      {/* The Whole Shebang */}
      <div className="bg-gradient-to-r from-blue-950 to-indigo-950 border border-blue-800 rounded-xl p-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-white">The Whole Shebang</h2>
            <p className="text-blue-300 text-sm mt-0.5">
              {allInstalled
                ? `All ${addons.length} modules installed.`
                : `Install all ${addons.length} modules (${(totalSize / 1000).toFixed(1)} GB total). Go make coffee.`}
            </p>
          </div>
          <button
            onClick={installAll}
            disabled={!!installing || allInstalled}
            className={`px-5 py-2.5 rounded-lg font-semibold text-sm transition-all ${
              allInstalled
                ? "bg-green-900/50 text-green-400 cursor-default"
                : installing === "all"
                ? "bg-blue-800 text-blue-300 animate-pulse"
                : "bg-blue-600 hover:bg-blue-500 text-white"
            }`}
          >
            {allInstalled ? "All Set" : installing === "all" ? "Installing..." : "Install Everything"}
          </button>
        </div>
        <div className="mt-3 flex gap-2 flex-wrap">
          {addons.map(a => (
            <span
              key={a.id}
              className={`text-xs px-2 py-0.5 rounded ${
                a.installed ? "bg-green-900/40 text-green-400" : "bg-zinc-800 text-zinc-500"
              }`}
            >
              {a.installed ? "\u2713" : "\u25CB"} {a.name}
            </span>
          ))}
        </div>
      </div>

      {/* Or pick what you need */}
      <div className="text-zinc-500 text-xs font-medium uppercase tracking-wider">
        Or pick what you need
      </div>

      {/* Individual cards */}
      <div className="space-y-3">
        {addons.map(addon => (
          <div
            key={addon.id}
            className={`border rounded-xl p-4 transition-all ${
              addon.installed
                ? "bg-zinc-900/50 border-green-900/50"
                : "bg-zinc-900 border-zinc-800"
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-white">{addon.name}</h3>
                  {addon.installed && (
                    <span className="text-xs bg-green-900/40 text-green-400 px-1.5 py-0.5 rounded">
                      installed
                    </span>
                  )}
                  <span className="text-xs text-zinc-600">
                    {addon.size_mb >= 1000
                      ? `${(addon.size_mb / 1000).toFixed(1)} GB`
                      : `${addon.size_mb} MB`}
                  </span>
                </div>
                <p className="text-zinc-400 text-sm mt-1">{addon.description}</p>
                <div className="flex gap-1.5 mt-2 flex-wrap">
                  {addon.features.map(f => (
                    <span key={f} className="text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded">
                      {f}
                    </span>
                  ))}
                </div>
              </div>
              <div className="flex-shrink-0">
                {addon.installed ? (
                  <button
                    onClick={() => uninstallOne(addon.id)}
                    disabled={!!installing}
                    className="px-3 py-1.5 text-xs rounded-lg bg-zinc-800 text-zinc-400 hover:bg-red-900/50 hover:text-red-400 transition-all"
                  >
                    Remove
                  </button>
                ) : (
                  <button
                    onClick={() => installOne(addon.id)}
                    disabled={!!installing}
                    className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                      installing === addon.id
                        ? "bg-blue-900 text-blue-300 animate-pulse"
                        : "bg-blue-600 hover:bg-blue-500 text-white"
                    }`}
                  >
                    {installing === addon.id ? "Installing..." : "Install"}
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
