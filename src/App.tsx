import { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';
import PrecursorDetail from '@/pages/PrecursorDetail';
import ReportDetail from '@/pages/ReportDetail';
import ReportsList from '@/pages/ReportsList';
import SubmitReport from '@/pages/SubmitReport';
import { CustomCursor } from '@/components/common/CustomCursor';

// three.js is ~130KB gzipped and the backdrop is purely decorative, so it
// loads in its own chunk after the dashboard is already interactive.
const AmbientField = lazy(() =>
  import('@/components/common/AmbientField').then((m) => ({ default: m.AmbientField }))
);

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={null}>
        <AmbientField />
      </Suspense>
      <CustomCursor />
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/submit" element={<SubmitReport />} />
        <Route path="/precursors/:id" element={<PrecursorDetail />} />
        <Route path="/reports" element={<ReportsList />} />
        <Route path="/reports/:id" element={<ReportDetail />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

