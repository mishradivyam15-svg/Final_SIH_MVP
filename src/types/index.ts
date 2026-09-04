/**
 * Stable frontend domain model.
 *
 * IMPORTANT: Components should only ever depend on these types.
 * Raw backend / mock payloads are converted into this shape by the
 * normalization functions in `src/services/adapters.ts`. If the backend
 * team changes field names or response structure, only the adapters
 * need to change — not the components or pages.
 */

export type Priority = 'HIGH' | 'MEDIUM' | 'LOW';

export type PrecursorStatus =
  | 'OPEN'
  | 'UNDER_INVESTIGATION'
  | 'CONFIRMED'
  | 'DISMISSED';

export type RelationshipType =
  | 'semantic_similarity'
  | 'same_hazard'
  | 'same_activity'
  | 'same_barrier'
  | 'same_site'
  | 'temporal_recurrence'
  | 'other';

export type ReportType =
  | 'UNSAFE_ACT'
  | 'UNSAFE_CONDITION'
  | 'NEAR_MISS';

/** A single safety report, after preprocessing / signal extraction. */
export interface SafetyReport {
  id: string;
  displayId: string; // e.g. "Report #1024"
  type: ReportType;
  date: string; // ISO date string
  site: string;
  activity: string;
  hazard: string;
  equipment?: string;
  barrier?: string;
  cause?: string;
  exposure?: string;
  narrative: string;
  /** Structured signals extracted by the AI/ML preprocessing pipeline. */
  signals: ExtractedSignal[];
  /** IDs of precursor patterns this report contributes to. */
  precursorIds: string[];
  /** Similarity/relationship strength to the precursor being viewed, 0-1. Optional context field. */
  relationshipScore?: number;
}

export interface ExtractedSignal {
  label: string;
  value: string;
  /** Optional confidence 0-1 from the extraction model, if supplied by the API. */
  confidence?: number;
}

/** A node in the cross-report relationship graph. */
export interface GraphNode {
  id: string;
  type: 'report' | 'precursor';
  label: string;
  sublabel?: string;
}

/** An edge (relationship) between two graph nodes. */
export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relationship: RelationshipType;
  /** Relationship strength, 0-1, when available (e.g. semantic similarity score). */
  strength?: number;
  label?: string;
}

export interface RelationshipGraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/** Explainability evidence backing a precursor alert. */
export interface Evidence {
  semanticSimilarity?: number; // 0-1
  hazardMatch?: boolean;
  activityMatch?: boolean;
  barrierMatch?: boolean;
  siteMatch?: boolean;
  temporalRecurrence?: 'LOW' | 'MEDIUM' | 'HIGH';
  contributingReportCount: number;
  recurrenceWindowDays?: number;
  summaryPoints: string[]; // human-readable "why flagged" bullet points
}

/** A recurring SIF precursor pattern grouping multiple related reports. */
export interface Precursor {
  id: string;
  title: string;
  priority: Priority;
  riskScore: number; // 0-100
  status: PrecursorStatus;
  hazard: string;
  activity: string;
  barrierFailure: string;
  site: string;
  reportCount: number;
  recurrenceWindowDays: number;
  shortExplanation: string;
  evidence: Evidence;
  reportIds: string[];
  createdAt: string; // ISO date
  updatedAt: string; // ISO date
  reviewHistory: ReviewEvent[];
}

export interface ReviewEvent {
  id: string;
  action: 'CONFIRM' | 'DISMISS' | 'INVESTIGATE';
  note?: string;
  actor?: string;
  timestamp: string; // ISO date
}

export interface DashboardOverview {
  reportsAnalyzed: number;
  precursorPatternCount: number;
  highPriorityCount: number;
  reviewQueueCount: number;
  lastUpdated: string; // ISO date
}

export interface DashboardData {
  overview: DashboardOverview;
  topPrecursor: Precursor | null;
  precursors: Precursor[];
  reviewQueue: Precursor[];
  isDemoData: boolean;
}

export interface PrecursorFilters {
  search?: string;
  priority?: Priority | 'ALL';
  site?: string | 'ALL';
  hazard?: string | 'ALL';
  activity?: string | 'ALL';
  status?: PrecursorStatus | 'ALL';
}

export type ReviewAction = 'CONFIRM' | 'DISMISS' | 'INVESTIGATE';

export interface SubmitReviewPayload {
  action: ReviewAction;
  note?: string;
}

/** Generic async resource wrapper used by data-fetching hooks. */
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}
