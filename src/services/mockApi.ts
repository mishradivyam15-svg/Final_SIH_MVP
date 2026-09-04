/**
 * Mock API service (used when VITE_USE_MOCK_DATA=true).
 *
 * Exposes the SAME function signatures as `src/services/api.ts` so the rest
 * of the app can depend on `src/services/dataService.ts` without caring
 * which implementation is active. Simulates network latency so
 * loading states can be demoed/tested honestly.
 */

import type {
  DashboardData,
  Precursor,
  SafetyReport,
  RelationshipGraphData,
  PrecursorFilters,
  SubmitReviewPayload,
  ReviewEvent,
  ReviewAction,
} from '@/types';
import {
  mockReports,
  mockPrecursors,
  mockOverview,
  mockRelationshipGraphs,
} from '@/data/mockData';
import { ApiError } from './api';

const LATENCY_MS = 450;

// Session-scoped mutable copy so review actions survive navigation and page
// refreshes during the demo, while remaining isolated to this browser session.
const REVIEW_STATE_KEY = 'neuronexus-demo-precursor-state-v1';

function loadInitialState(): Precursor[] {
  if (typeof window === 'undefined') return mockPrecursors.map((p) => ({ ...p }));
  try {
    const stored = window.sessionStorage.getItem(REVIEW_STATE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored) as unknown;
      if (Array.isArray(parsed)) return parsed as Precursor[];
    }
  } catch {
    // Fall back to the source demo data if sessionStorage is unavailable/corrupt.
  }
  return mockPrecursors.map((p) => ({ ...p }));
}

function persistState(state: Precursor[]): void {
  if (typeof window === 'undefined') return;
  try {
    window.sessionStorage.setItem(REVIEW_STATE_KEY, JSON.stringify(state));
  } catch {
    // In-memory state still works if browser storage is unavailable.
  }
}

let precursorState: Precursor[] = loadInitialState();

function delay<T>(value: T, ms = LATENCY_MS): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms));
}

function matchesFilters(p: Precursor, filters?: PrecursorFilters): boolean {
  if (!filters) return true;
  const { search, priority, site, hazard, activity, status } = filters;

  if (search && search.trim()) {
    const q = search.trim().toLowerCase();
    const haystack = `${p.title} ${p.hazard} ${p.activity} ${p.barrierFailure} ${p.site}`.toLowerCase();
    if (!haystack.includes(q)) return false;
  }
  if (priority && priority !== 'ALL' && p.priority !== priority) return false;
  if (site && site !== 'ALL' && p.site !== site) return false;
  if (hazard && hazard !== 'ALL' && p.hazard !== hazard) return false;
  if (activity && activity !== 'ALL' && p.activity !== activity) return false;
  if (status && status !== 'ALL' && p.status !== status) return false;
  return true;
}

// ---------------------------------------------------------------------------
// Mirrors src/services/api.ts
// ---------------------------------------------------------------------------

export async function getDashboard(): Promise<DashboardData> {
  const highPriority = precursorState.filter((p) => p.priority === 'HIGH');
  const overview = {
    ...mockOverview,
    precursorPatternCount: precursorState.length,
    highPriorityCount: highPriority.length,
    reviewQueueCount: precursorState.filter(
      (p) => p.status === 'OPEN' || p.status === 'UNDER_INVESTIGATION'
    ).length,
  };

  const topPrecursor =
    [...precursorState].sort((a, b) => b.riskScore - a.riskScore)[0] ?? null;

  const reviewQueue = precursorState.filter(
    (p) => p.status === 'OPEN' || p.status === 'UNDER_INVESTIGATION'
  );

  return delay({
    overview,
    topPrecursor,
    precursors: precursorState,
    reviewQueue,
    isDemoData: true,
  });
}

export async function getPrecursors(filters?: PrecursorFilters): Promise<Precursor[]> {
  return delay(precursorState.filter((p) => matchesFilters(p, filters)));
}

export async function getPrecursor(id: string): Promise<Precursor> {
  const found = precursorState.find((p) => p.id === id);
  if (!found) {
    throw new ApiError(`Precursor "${id}" was not found in the demo dataset.`, 404);
  }
  return delay({ ...found });
}

export async function getRelationships(id: string): Promise<RelationshipGraphData> {
  const graph = mockRelationshipGraphs[id];
  return delay(graph ?? { nodes: [], edges: [] });
}

export async function getReport(id: string): Promise<SafetyReport> {
  const found = mockReports.find((r) => r.id === id);
  if (!found) {
    throw new ApiError(`Report "${id}" was not found in the demo dataset.`, 404);
  }
  return delay({ ...found });
}

export async function getReportsByIds(ids: string[]): Promise<SafetyReport[]> {
  const found = mockReports.filter((r) => ids.includes(r.id));
  return delay(found);
}

export async function submitReview(
  precursorId: string,
  payload: SubmitReviewPayload
): Promise<ReviewEvent> {
  const index = precursorState.findIndex((p) => p.id === precursorId);
  if (index === -1) {
    throw new ApiError(`Precursor "${precursorId}" was not found.`, 404);
  }

  const statusByAction: Record<ReviewAction, Precursor['status']> = {
    CONFIRM: 'CONFIRMED',
    DISMISS: 'DISMISSED',
    INVESTIGATE: 'UNDER_INVESTIGATION',
  };

  const event: ReviewEvent = {
    id: `ev-${Date.now()}`,
    action: payload.action,
    note: payload.note,
    actor: 'HSE Reviewer (Demo)',
    timestamp: new Date().toISOString(),
  };

  const updated: Precursor = {
    ...precursorState[index],
    status: statusByAction[payload.action],
    updatedAt: new Date().toISOString().slice(0, 10),
    reviewHistory: [...precursorState[index].reviewHistory, event],
  };

  precursorState = [
    ...precursorState.slice(0, index),
    updated,
    ...precursorState.slice(index + 1),
  ];
  persistState(precursorState);

  return delay(event);
}

/** Test/demo utility: restore the original mock dataset (e.g. between demo runs). */
export function resetMockState(): void {
  precursorState = mockPrecursors.map((p) => ({ ...p }));
  if (typeof window !== 'undefined') {
    try {
      window.sessionStorage.removeItem(REVIEW_STATE_KEY);
    } catch {
      // Ignore storage failures; in-memory state has already been reset.
    }
  }
}
