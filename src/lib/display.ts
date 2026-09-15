import type { Priority, PrecursorStatus, RelationshipType, ReportType } from '@/types';

export const PRIORITY_LABEL: Record<Priority, string> = {
  HIGH: 'High',
  MEDIUM: 'Medium',
  LOW: 'Low',
};

export const PRIORITY_CLASSES: Record<Priority, { bg: string; text: string; border: string; dot: string }> = {
  HIGH: {
    bg: 'bg-priority-highBg',
    text: 'text-priority-high',
    border: 'border-priority-highBorder',
    dot: 'bg-priority-high',
  },
  MEDIUM: {
    bg: 'bg-priority-mediumBg',
    text: 'text-priority-medium',
    border: 'border-priority-mediumBorder',
    dot: 'bg-priority-medium',
  },
  LOW: {
    bg: 'bg-priority-lowBg',
    text: 'text-priority-low',
    border: 'border-priority-lowBorder',
    dot: 'bg-priority-low',
  },
};

export const STATUS_LABEL: Record<PrecursorStatus, string> = {
  OPEN: 'New',
  UNDER_INVESTIGATION: 'Under Investigation',
  CONFIRMED: 'Confirmed',
  DISMISSED: 'Dismissed',
};

export const STATUS_CLASSES: Record<PrecursorStatus, { bg: string; text: string }> = {
  OPEN: { bg: 'bg-status-openBg', text: 'text-status-open' },
  UNDER_INVESTIGATION: { bg: 'bg-status-investigatingBg', text: 'text-status-investigating' },
  CONFIRMED: { bg: 'bg-status-confirmedBg', text: 'text-status-confirmed' },
  DISMISSED: { bg: 'bg-status-dismissedBg', text: 'text-status-dismissed' },
};

export const REPORT_TYPE_LABEL: Record<ReportType, string> = {
  UNSAFE_ACT: 'Unsafe Act',
  UNSAFE_CONDITION: 'Unsafe Condition',
  NEAR_MISS: 'Near Miss',
};

export const RELATIONSHIP_LABEL: Record<RelationshipType, string> = {
  semantic_similarity: 'Semantic similarity',
  same_hazard: 'Same hazard',
  same_activity: 'Same activity',
  same_barrier: 'Same barrier',
  same_site: 'Same site',
  temporal_recurrence: 'Temporal recurrence',
  other: 'Related',
};

export const RELATIONSHIP_COLOR: Record<RelationshipType, string> = {
  semantic_similarity: '#5b9bd9',
  same_hazard: '#f87171',
  same_activity: '#fbbf24',
  same_barrier: '#b794f6',
  same_site: '#4ade80',
  temporal_recurrence: '#2dd4bf',
  other: '#8a93a1',
};

export function riskScoreToPriority(score: number): Priority {
  if (score >= 75) return 'HIGH';
  if (score >= 45) return 'MEDIUM';
  return 'LOW';
}
