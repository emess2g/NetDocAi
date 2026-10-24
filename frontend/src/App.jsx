
import { BrowserRouter, Routes, Route } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import DashboardLayout from "./layouts/DashboardLayout";

import Home from "./pages/Home";
import Analyze from "./pages/Analyze";
import Dashboard from "./pages/Dashboard";
import DashboardOverview from "./pages/DashboardOverview";
import Documentation from "./pages/Documentation";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ProtectedRoute from "./components/ProtectedRoute";
import History from "./pages/History";

function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#070b12] px-6 text-white">
      <div className="text-center">
        <p className="text-sm font-medium text-blue-400">404</p>

        <h1 className="mt-2 text-3xl font-bold">Page not found</h1>

        <p className="mt-3 text-sm text-slate-500">
          The page you're looking for doesn't exist.
        </p>

        <a
          href="/"
          className="mt-6 inline-flex rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Back to NetDocAI
        </a>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Main application layout */}
        <Route element={<AppLayout />}>
          <Route path="/" element={<Home />} />

        </Route>

        {/* Dashboard workspace follows the Figma sidebar layout and keeps reports under the same shell. */}
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard" element={<ProtectedRoute><DashboardOverview /></ProtectedRoute>} />
          <Route path="/dashboard/:analysisId" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/analyze" element={<ProtectedRoute><Analyze /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
          <Route path="/docs" element={<Documentation />} />
        </Route>

        {/* Authentication pages */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

