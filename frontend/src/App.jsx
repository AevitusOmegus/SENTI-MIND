import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardLayout from "./pages/DashboardLayout";
import JournalPage from "./pages/JournalPage";
import MoodHeatmapPage from "./pages/MoodHeatmapPage";
import HistoryPage from "./pages/HistoryPage";
import GratitudeJarPage from "./pages/GratitudeJarPage";
import ScreenerPage from "./pages/ScreenerPage";
import WellnessToolsPage from "./pages/WellnessToolsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<JournalPage />} />
        <Route path="heatmap" element={<MoodHeatmapPage />} />
        <Route path="history" element={<HistoryPage />} />
        <Route path="gratitude" element={<GratitudeJarPage />} />
        <Route path="screener" element={<ScreenerPage />} />
        <Route path="wellness" element={<WellnessToolsPage />} />
      </Route>

      {/* Default redirect */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
