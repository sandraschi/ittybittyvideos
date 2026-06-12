import { NavLink } from "react-router-dom";
import {
  BookMarked,
  Clapperboard,
  Film,
  HelpCircle,
  LayoutDashboard,
  Library,
  ListVideo,
  MessageSquare,
  Radio,
  ScrollText,
  Settings,
  Share2,
  Sparkles,
  Wrench,
  Code2,
  Activity,
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/generate", label: "Short video", icon: Sparkles },
  { to: "/plan", label: "Mid-length", icon: Film },
  { to: "/prompts", label: "Prompt library", icon: BookMarked },
  { to: "/jobs", label: "Jobs", icon: ListVideo },
  { to: "/depot", label: "Depot", icon: Library },
  { to: "/publish", label: "Publish", icon: Share2 },
  { to: "/tools", label: "Tools", icon: Wrench },
  { to: "/chat", label: "Chat", icon: MessageSquare },
  { to: "/status", label: "Status", icon: Activity },
  { to: "/settings", label: "Settings", icon: Settings },
  { to: "/logs", label: "Logs", icon: ScrollText },
  { to: "/api-docs", label: "API Docs", icon: Code2 },
  { to: "/help", label: "Help", icon: HelpCircle },
];

export default function Sidebar() {
  return (
    <nav className="w-52 shrink-0 border-r border-zinc-800 bg-zinc-900/90 backdrop-blur p-3 flex flex-col gap-1">
      <div className="flex items-center gap-2 px-2 py-3 mb-2">
        <Clapperboard className="w-5 h-5 text-blue-500" />
        <div>
          <p className="text-sm font-bold tracking-tight">ittybitty</p>
          <p className="text-[10px] text-zinc-500">videogen-mcp</p>
        </div>
      </div>
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            `flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
              isActive
                ? "bg-blue-600/90 text-white"
                : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
            }`
          }
        >
          <Icon className="w-4 h-4 shrink-0" />
          <span>{label}</span>
        </NavLink>
      ))}
      <div className="mt-auto pt-4 px-2 text-[10px] text-zinc-600 flex items-center gap-1">
        <Radio className="w-3 h-3" />
        :11054 / :11055
      </div>
    </nav>
  );
}
