/**
 * Real API service layer (used when VITE_USE_MOCK_DATA=false).
 *
 * All network calls live here — components never call fetch() directly.
 * Every function returns data already normalized into the stable frontend
 * model (see src/types and src/services/adapters.ts), so callers don't
 * need to know whether the data came from mock or a live backend.
 */

import type {
  DashboardData,
  Precursor,
  SafetyReport,
  RelationshipGraphData,
  PrecursorFilters,
  SubmitReviewPayload,
  ReviewEvent,
  ReportSubmission,
  AnalysisResponse,
} from '@/types';
import {
  normalizeDashboard,
  normalizePrecursor,
  normalizeReport,
  normalizeRelationshipGraph,
  normalizeReviewEvent,
} from './adapters';

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(
  /\/$/,
  ''
) || 'http://localhost:8000';

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T = unknown>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
  } catch {
    throw new ApiError(
      'Could not reach the backend service. Please check your connection or try again.'
    );
  }

  if (!response.ok) {
    throw new ApiError(
      `Request to ${path} failed with status ${response.status}.`,
      response.status
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError('Received an unreadable response from the server.');
  }
}

function buildQuery(filters?: PrecursorFilters): string {
  if (!filters) return '';
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value && value !== 'ALL') params.set(key, String(value));
  });
  const qs = params.toString();
  return qs ? `?${qs}` : '';
}

// ---------------------------------------------------------------------------
// Public API — endpoint paths documented in README.md
// ---------------------------------------------------------------------------

/** GET /api/dashboard */
export async function getDashboard(): Promise<DashboardData> {
  const raw = await request('/api/dashboard');
  return normalizeDashboard(raw);
}

/** GET /api/precursors */
export async function getPrecursors(filters?: PrecursorFilters): Promise<Precursor[]> {
  const raw = await request<unknown[]>(`/api/precursors${buildQuery(filters)}`);
  return Array.isArray(raw) ? raw.map(normalizePrecursor) : [];
}

/** GET /api/precursors/:id */
export async function getPrecursor(id: string): Promise<Precursor> {
  const raw = await request(`/api/precursors/${encodeURIComponent(id)}`);
  return normalizePrecursor(raw);
}

/** GET /api/precursors/:id/relationships */
export async function getRelationships(id: string): Promise<RelationshipGraphData> {
  const raw = await request(`/api/precursors/${encodeURIComponent(id)}/relationships`);
  return normalizeRelationshipGraph(raw);
}

/** GET /api/reports/:id */
export async function getReport(id: string): Promise<SafetyReport> {
  const raw = await request(`/api/reports/${encodeURIComponent(id)}`);
  return normalizeReport(raw);
}

/** GET /api/reports?ids=... (used to hydrate contributing reports) */
export async function getReportsByIds(ids: string[]): Promise<SafetyReport[]> {
  if (ids.length === 0) return [];
  const raw = await request<unknown[]>(
    `/api/reports?ids=${ids.map(encodeURIComponent).join(',')}`
  );
  return Array.isArray(raw) ? raw.map(normalizeReport) : [];
}

/** GET /api/reports (no ids) — every report analyzed so far, most recent first */
export async function getAllReports(): Promise<SafetyReport[]> {
  const raw = await request<unknown[]>('/api/reports');
  return Array.isArray(raw) ? raw.map(normalizeReport) : [];
}

/** POST /api/review */
export async function submitReview(
  precursorId: string,
  payload: SubmitReviewPayload
): Promise<ReviewEvent> {
  const raw = await request(`/api/precursors/${encodeURIComponent(precursorId)}/review`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return normalizeReviewEvent(raw);
}

// ---------------------------------------------------------------------------
// Report submission → backend extraction pipeline
// ---------------------------------------------------------------------------

/** POST /api/v1/reports/analyze — submit a report to the real backend */
export async function submitReport(payload: ReportSubmission): Promise<AnalysisResponse> {
  return request<AnalysisResponse>('/api/v1/reports/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

