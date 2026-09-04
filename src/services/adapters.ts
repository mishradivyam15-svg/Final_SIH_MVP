/**
 * Normalization layer.
 *
 * backend / mock response → normalize*() → stable frontend model (src/types)
 *
 * Components and pages NEVER read raw API/mock payloads directly — they only
 * consume the types defined in `src/types/index.ts`. If the backend team
 * changes field names, response envelopes, or nesting, only the functions in
 * this file need to change.
 *
 * Each normalizer is defensive: it tolerates missing/renamed fields and
 * fills in safe defaults rather than throwing, so an incomplete backend
 * response cannot crash the UI.
 */

import type {
  SafetyReport,
  Precursor,
  DashboardData,
  DashboardOverview,
  RelationshipGraphData,
  GraphNode,
  GraphEdge,
  ExtractedSignal,
  Evidence,
  ReviewEvent,
  Priority,
  PrecursorStatus,
  ReportType,
  RelationshipType,
} from '@/types';

// ---------------------------------------------------------------------------
// Small safe-coercion helpers
// ---------------------------------------------------------------------------

const asString = (v: unknown, fallback = ''): string =>
  typeof v === 'string' ? v : v == null ? fallback : String(v);

const asNumber = (v: unknown, fallback = 0): number => {
  const n = typeof v === 'number' ? v : Number(v);
  return Number.isFinite(n) ? n : fallback;
};

const asBoolOrUndefined = (v: unknown): boolean | undefined =>
  typeof v === 'boolean' ? v : undefined;

const asArray = <T,>(v: unknown): T[] => (Array.isArray(v) ? (v as T[]) : []);

const ALLOWED_PRIORITIES: Priority[] = ['HIGH', 'MEDIUM', 'LOW'];
const normalizePriority = (v: unknown): Priority => {
  const s = asString(v).toUpperCase();
  return (ALLOWED_PRIORITIES as string[]).includes(s) ? (s as Priority) : 'LOW';
};

const ALLOWED_STATUSES: PrecursorStatus[] = [
  'OPEN',
  'UNDER_INVESTIGATION',
  'CONFIRMED',
  'DISMISSED',
];
const normalizeStatus = (v: unknown): PrecursorStatus => {
  const s = asString(v).toUpperCase().replace(/\s+/g, '_');
  return (ALLOWED_STATUSES as string[]).includes(s) ? (s as PrecursorStatus) : 'OPEN';
};

const ALLOWED_REPORT_TYPES: ReportType[] = ['UNSAFE_ACT', 'UNSAFE_CONDITION', 'NEAR_MISS'];
const normalizeReportType = (v: unknown): ReportType => {
  const s = asString(v).toUpperCase().replace(/\s+/g, '_');
  return (ALLOWED_REPORT_TYPES as string[]).includes(s) ? (s as ReportType) : 'NEAR_MISS';
};

const ALLOWED_RELATIONSHIPS: RelationshipType[] = [
  'semantic_similarity',
  'same_hazard',
  'same_activity',
  'same_barrier',
  'same_site',
  'temporal_recurrence',
  'other',
];
const normalizeRelationshipType = (v: unknown): RelationshipType => {
  const s = asString(v).toLowerCase().replace(/\s+/g, '_');
  return (ALLOWED_RELATIONSHIPS as string[]).includes(s)
    ? (s as RelationshipType)
    : 'other';
};

// ---------------------------------------------------------------------------
// Report
// ---------------------------------------------------------------------------

export function normalizeSignal(raw: unknown): ExtractedSignal {
  const r = (raw ?? {}) as Record<string, unknown>;
  return {
    label: asString(r.label ?? r.name, 'Signal'),
    value: asString(r.value, '—'),
    confidence:
      typeof r.confidence === 'number' || typeof r.confidence === 'string'
        ? asNumber(r.confidence)
        : undefined,
  };
}

export function normalizeReport(raw: unknown): SafetyReport {
  const r = (raw ?? {}) as Record<string, unknown>;
  const id = asString(r.id ?? r.report_id, 'UNKNOWN');
  return {
    id,
    displayId: asString(r.displayId ?? r.display_id, `Report #${id}`),
    type: normalizeReportType(r.type ?? r.report_type),
    date: asString(r.date ?? r.reported_at, ''),
    site: asString(r.site ?? r.location, 'Unknown site'),
    activity: asString(r.activity, 'Unknown activity'),
    hazard: asString(r.hazard, 'Unknown hazard'),
    equipment: r.equipment != null ? asString(r.equipment) : undefined,
    barrier:
      r.barrier != null || r.barrier_failure != null
        ? asString(r.barrier ?? r.barrier_failure)
        : undefined,
    cause: r.cause != null ? asString(r.cause) : undefined,
    exposure: r.exposure != null ? asString(r.exposure) : undefined,
    narrative: asString(r.narrative ?? r.text ?? r.description, ''),
    signals: asArray(r.signals ?? r.extracted_signals).map(normalizeSignal),
    precursorIds: asArray<unknown>(r.precursorIds ?? r.precursor_ids).map((v) =>
      asString(v)
    ),
    relationshipScore:
      typeof r.relationshipScore === 'number' || typeof r.relationshipScore === 'string' ||
        typeof r.relationship_score === 'number' || typeof r.relationship_score === 'string'
        ? asNumber(r.relationshipScore ?? r.relationship_score)
        : undefined,
  };
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------

export function normalizeEvidence(raw: unknown): Evidence {
  const r = (raw ?? {}) as Record<string, unknown>;
  const temporalRaw = asString(
    r.temporalRecurrence ?? r.temporal_recurrence,
    ''
  ).toUpperCase();
  const temporalRecurrence: Evidence['temporalRecurrence'] =
    temporalRaw === 'HIGH' || temporalRaw === 'MEDIUM' || temporalRaw === 'LOW'
      ? (temporalRaw as 'HIGH' | 'MEDIUM' | 'LOW')
      : undefined;

  return {
    semanticSimilarity:
      typeof r.semanticSimilarity === 'number' || typeof r.semanticSimilarity === 'string' ||
        typeof r.semantic_similarity === 'number' || typeof r.semantic_similarity === 'string'
        ? asNumber(r.semanticSimilarity ?? r.semantic_similarity)
        : undefined,
    hazardMatch: asBoolOrUndefined(r.hazardMatch ?? r.hazard_match),
    activityMatch: asBoolOrUndefined(r.activityMatch ?? r.activity_match),
    barrierMatch: asBoolOrUndefined(r.barrierMatch ?? r.barrier_match),
    siteMatch: asBoolOrUndefined(r.siteMatch ?? r.site_match),
    temporalRecurrence,
    contributingReportCount: asNumber(
      r.contributingReportCount ?? r.contributing_report_count,
      0
    ),
    recurrenceWindowDays:
      typeof r.recurrenceWindowDays === 'number' || typeof r.recurrenceWindowDays === 'string' ||
        typeof r.recurrence_window_days === 'number' || typeof r.recurrence_window_days === 'string'
        ? asNumber(r.recurrenceWindowDays ?? r.recurrence_window_days)
        : undefined,
    summaryPoints: asArray<unknown>(r.summaryPoints ?? r.summary_points).map((v) =>
      asString(v)
    ),
  };
}

// ---------------------------------------------------------------------------
// Review events
// ---------------------------------------------------------------------------

export function normalizeReviewEvent(raw: unknown): ReviewEvent {
  const r = (raw ?? {}) as Record<string, unknown>;
  const actionRaw = asString(r.action).toUpperCase();
  const action: ReviewEvent['action'] =
    actionRaw === 'CONFIRM' || actionRaw === 'DISMISS' || actionRaw === 'INVESTIGATE'
      ? actionRaw
      : 'INVESTIGATE';
  return {
    id: asString(r.id, `ev-${Math.random().toString(36).slice(2, 9)}`),
    action,
    note: r.note != null ? asString(r.note) : undefined,
    actor: r.actor != null ? asString(r.actor) : undefined,
    timestamp: asString(r.timestamp ?? r.created_at, new Date().toISOString()),
  };
}

// ---------------------------------------------------------------------------
// Precursor
// ---------------------------------------------------------------------------

export function normalizePrecursor(raw: unknown): Precursor {
  const r = (raw ?? {}) as Record<string, unknown>;
  return {
    id: asString(r.id ?? r.precursor_id, 'UNKNOWN'),
    title: asString(r.title ?? r.name, 'Untitled precursor'),
    priority: normalizePriority(r.priority),
    riskScore: asNumber(r.riskScore ?? r.risk_score, 0),
    status: normalizeStatus(r.status),
    hazard: asString(r.hazard, 'Unknown hazard'),
    activity: asString(r.activity, 'Unknown activity'),
    barrierFailure: asString(r.barrierFailure ?? r.barrier_failure, 'Unknown barrier'),
    site: asString(r.site ?? r.location, 'Unknown site'),
    reportCount: asNumber(
      r.reportCount ?? r.report_count ?? asArray(r.reportIds ?? r.report_ids).length,
      0
    ),
    recurrenceWindowDays: asNumber(
      r.recurrenceWindowDays ?? r.recurrence_window_days,
      0
    ),
    shortExplanation: asString(r.shortExplanation ?? r.short_explanation, ''),
    evidence: normalizeEvidence(r.evidence),
    reportIds: asArray<unknown>(r.reportIds ?? r.report_ids).map((v) => asString(v)),
    createdAt: asString(r.createdAt ?? r.created_at, ''),
    updatedAt: asString(r.updatedAt ?? r.updated_at, ''),
    reviewHistory: asArray(r.reviewHistory ?? r.review_history).map(normalizeReviewEvent),
  };
}

// ---------------------------------------------------------------------------
// Dashboard overview
// ---------------------------------------------------------------------------

export function normalizeOverview(raw: unknown): DashboardOverview {
  const r = (raw ?? {}) as Record<string, unknown>;
  return {
    reportsAnalyzed: asNumber(r.reportsAnalyzed ?? r.reports_analyzed, 0),
    precursorPatternCount: asNumber(
      r.precursorPatternCount ?? r.precursor_pattern_count,
      0
    ),
    highPriorityCount: asNumber(r.highPriorityCount ?? r.high_priority_count, 0),
    reviewQueueCount: asNumber(r.reviewQueueCount ?? r.review_queue_count, 0),
    lastUpdated: asString(r.lastUpdated ?? r.last_updated, ''),
  };
}

export function normalizeDashboard(raw: unknown): DashboardData {
  const r = (raw ?? {}) as Record<string, unknown>;
  const precursors = asArray(r.precursors).map(normalizePrecursor);
  return {
    overview: normalizeOverview(r.overview),
    topPrecursor: r.topPrecursor ?? r.top_precursor
      ? normalizePrecursor(r.topPrecursor ?? r.top_precursor)
      : precursors.find((p) => p.priority === 'HIGH') ?? precursors[0] ?? null,
    precursors,
    reviewQueue: asArray(r.reviewQueue ?? r.review_queue).map(normalizePrecursor),
    isDemoData: Boolean(r.isDemoData ?? r.is_demo_data ?? true),
  };
}

// ---------------------------------------------------------------------------
// Relationship graph
// ---------------------------------------------------------------------------

export function normalizeGraphNode(raw: unknown): GraphNode {
  const r = (raw ?? {}) as Record<string, unknown>;
  const typeRaw = asString(r.type).toLowerCase();
  return {
    id: asString(r.id, 'unknown-node'),
    type: typeRaw === 'precursor' ? 'precursor' : 'report',
    label: asString(r.label ?? r.name, asString(r.id, 'Node')),
    sublabel: r.sublabel != null ? asString(r.sublabel) : undefined,
  };
}

export function normalizeGraphEdge(raw: unknown, index: number): GraphEdge {
  const r = (raw ?? {}) as Record<string, unknown>;
  return {
    id: asString(r.id, `edge-${index}`),
    source: asString(r.source ?? r.from, ''),
    target: asString(r.target ?? r.to, ''),
    relationship: normalizeRelationshipType(r.relationship ?? r.type),
    strength:
      typeof r.strength === 'number' || typeof r.weight === 'number'
        ? asNumber(r.strength ?? r.weight)
        : undefined,
    label: r.label != null ? asString(r.label) : undefined,
  };
}

export function normalizeRelationshipGraph(raw: unknown): RelationshipGraphData {
  const r = (raw ?? {}) as Record<string, unknown>;
  return {
    nodes: asArray(r.nodes).map(normalizeGraphNode),
    edges: asArray(r.edges).map((e, i) => normalizeGraphEdge(e, i)),
  };
}
