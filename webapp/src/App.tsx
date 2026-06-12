import { Routes, Route } from "react-router-dom";
import AppLayout from "@/components/layout/AppLayout";
import ApiDocs from "@/pages/api-docs";
import Chat from "@/pages/chat";
import Dashboard from "@/pages/dashboard";
import Generate from "@/pages/generate";
import Help from "@/pages/help";
import Logs from "@/pages/logs";
import Jobs from "@/pages/jobs";
import Depot from "@/pages/depot";
import Plan from "@/pages/plan";
import Publish from "@/pages/publish";
import SettingsPage from "@/pages/settings";
import StatusPage from "@/pages/status";
import Tools from "@/pages/tools";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/generate" element={<Generate />} />
        <Route path="/plan" element={<Plan />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/depot" element={<Depot />} />
        <Route path="/publish" element={<Publish />} />
        <Route path="/tools" element={<Tools />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/api-docs" element={<ApiDocs />} />
        <Route path="/logs" element={<Logs />} />
        <Route path="/help" element={<Help />} />
      </Route>
    </Routes>
  );
}
