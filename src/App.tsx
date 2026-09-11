import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';
import PrecursorDetail from '@/pages/PrecursorDetail';
import ReportDetail from '@/pages/ReportDetail';
import SubmitReport from '@/pages/SubmitReport';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/submit" element={<SubmitReport />} />
        <Route path="/precursors/:id" element={<PrecursorDetail />} />
        <Route path="/reports/:id" element={<ReportDetail />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

