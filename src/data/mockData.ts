/**
 * PROTOTYPE / REPRESENTATIVE DATA
 * ================================
 * Everything in this file is fabricated for demonstration purposes only.
 * None of these values (report counts, risk scores, recurrence windows,
 * similarity scores, etc.) represent real OIL India statistics or the
 * output of a trained model. They exist so the UI can be demoed and
 * tested before the AI/ML and backend components are integrated.
 *
 * This is the ONLY file that should contain hand-authored demo values.
 * Once the backend is ready, `src/services/mockApi.ts` is simply swapped
 * out for `src/services/api.ts` (see VITE_USE_MOCK_DATA in .env).
 */

import type {
  SafetyReport,
  Precursor,
  DashboardOverview,
  RelationshipGraphData,
} from '@/types';

// ---------------------------------------------------------------------------
// Raw safety reports
// ---------------------------------------------------------------------------

export const mockReports: SafetyReport[] = [
  {
    id: 'R1024',
    displayId: 'Report #1024',
    type: 'NEAR_MISS',
    date: '2026-07-21',
    site: 'Duliajan Field Site A',
    activity: 'Working at height',
    hazard: 'Fall from height',
    equipment: 'Scaffolding (mobile tower)',
    barrier: 'Missing fall protection',
    cause: 'Fall-arrest harness not anchored before ascent',
    exposure: 'Technician, ~6m elevation',
    narrative:
      'Technician was observed climbing mobile scaffolding to access a valve manifold without clipping the fall-arrest lanyard to an anchor point. A co-worker intervened before work began. No injury occurred.',
    signals: [
      { label: 'Hazard', value: 'Fall from height', confidence: 0.94 },
      { label: 'Activity', value: 'Working at height', confidence: 0.91 },
      { label: 'Barrier Failure', value: 'Missing fall protection', confidence: 0.89 },
      { label: 'Equipment', value: 'Mobile scaffolding tower', confidence: 0.86 },
    ],
    precursorIds: ['P-001'],
  },
  {
    id: 'R1088',
    displayId: 'Report #1088',
    type: 'UNSAFE_ACT',
    date: '2026-07-25',
    site: 'Duliajan Field Site A',
    activity: 'Working at height',
    hazard: 'Fall from height',
    equipment: 'Fixed ladder',
    barrier: 'Missing fall protection',
    cause: 'Harness available but not worn during ladder ascent',
    exposure: 'Contract worker, ~4m elevation',
    narrative:
      'During a routine site walk, a contract worker was found ascending a fixed ladder to a platform without a harness, despite one being issued for the task. Worker was instructed to stop and re-equip.',
    signals: [
      { label: 'Hazard', value: 'Fall from height', confidence: 0.92 },
      { label: 'Activity', value: 'Working at height', confidence: 0.9 },
      { label: 'Barrier Failure', value: 'Missing fall protection', confidence: 0.88 },
      { label: 'Equipment', value: 'Fixed access ladder', confidence: 0.81 },
    ],
    precursorIds: ['P-001'],
  },
  {
    id: 'R1112',
    displayId: 'Report #1112',
    type: 'UNSAFE_CONDITION',
    date: '2026-07-30',
    site: 'Duliajan Field Site A',
    activity: 'Working at height',
    hazard: 'Fall from height',
    equipment: 'Scaffolding',
    barrier: 'Missing fall protection',
    cause: 'Anchor points not installed on newly erected scaffold section',
    exposure: 'Multiple crew members, ~5-8m elevation',
    narrative:
      'A newly erected scaffold section on the eastern platform had no certified anchor points installed for fall-arrest systems. Crew flagged the gap before mounting the section for use.',
    signals: [
      { label: 'Hazard', value: 'Fall from height', confidence: 0.95 },
      { label: 'Activity', value: 'Working at height', confidence: 0.93 },
      { label: 'Barrier Failure', value: 'Missing fall protection', confidence: 0.9 },
      { label: 'Equipment', value: 'Scaffolding', confidence: 0.87 },
    ],
    precursorIds: ['P-001'],
  },
  {
    id: 'R1140',
    displayId: 'Report #1140',
    type: 'NEAR_MISS',
    date: '2026-08-04',
    site: 'Duliajan Field Site B',
    activity: 'Working at height',
    hazard: 'Fall from height',
    equipment: 'Scaffolding',
    barrier: 'Missing fall protection',
    cause: 'Guardrail section removed for material transfer, not reinstated',
    exposure: 'Technician, ~7m elevation',
    narrative:
      'A guardrail section was temporarily removed to transfer pipe fittings and was not reinstated before the platform was reoccupied. A technician nearly stepped through the open edge.',
    signals: [
      { label: 'Hazard', value: 'Fall from height', confidence: 0.93 },
      { label: 'Activity', value: 'Working at height', confidence: 0.89 },
      { label: 'Barrier Failure', value: 'Missing fall protection', confidence: 0.85 },
    ],
    precursorIds: ['P-001'],
  },
  {
    id: 'R1027',
    displayId: 'Report #1027',
    type: 'UNSAFE_CONDITION',
    date: '2026-07-22',
    site: 'Duliajan Field Site A',
    activity: 'Pipeline maintenance',
    hazard: 'Hydrocarbon release',
    equipment: 'Flange coupling',
    barrier: 'Inadequate isolation',
    cause: 'LOTO tag applied to wrong valve during isolation check',
    exposure: 'Maintenance crew, confined area',
    narrative:
      'During pre-maintenance isolation verification, the lock-out/tag-out tag was found on an adjacent valve rather than the intended isolation point, which would not have isolated the line as required.',
    signals: [
      { label: 'Hazard', value: 'Hydrocarbon release', confidence: 0.88 },
      { label: 'Activity', value: 'Pipeline maintenance', confidence: 0.9 },
      { label: 'Barrier Failure', value: 'Inadequate isolation (LOTO)', confidence: 0.86 },
    ],
    precursorIds: ['P-002'],
  },
  {
    id: 'R1055',
    displayId: 'Report #1055',
    type: 'NEAR_MISS',
    date: '2026-07-27',
    site: 'Duliajan Field Site A',
    activity: 'Pipeline maintenance',
    hazard: 'Hydrocarbon release',
    equipment: 'Isolation valve',
    barrier: 'Inadequate isolation',
    cause: 'Isolation checklist step skipped under time pressure',
    exposure: 'Maintenance crew',
    narrative:
      'Crew reported skipping a double-block-and-bleed verification step to meet a shift changeover deadline. A supervisor caught the gap during the permit closeout review.',
    signals: [
      { label: 'Hazard', value: 'Hydrocarbon release', confidence: 0.85 },
      { label: 'Activity', value: 'Pipeline maintenance', confidence: 0.88 },
      { label: 'Barrier Failure', value: 'Inadequate isolation (LOTO)', confidence: 0.83 },
    ],
    precursorIds: ['P-002'],
  },
  {
    id: 'R1071',
    displayId: 'Report #1071',
    type: 'UNSAFE_ACT',
    date: '2026-08-02',
    site: 'Duliajan Field Site A',
    activity: 'Pipeline maintenance',
    hazard: 'Hydrocarbon release',
    equipment: 'Flange coupling',
    barrier: 'Inadequate isolation',
    cause: 'Permit-to-work closed without independent isolation verification',
    exposure: 'Maintenance crew',
    narrative:
      'Permit-to-work was signed off by the same technician who performed the isolation, without the required second-person independent verification.',
    signals: [
      { label: 'Hazard', value: 'Hydrocarbon release', confidence: 0.87 },
      { label: 'Activity', value: 'Pipeline maintenance', confidence: 0.86 },
      { label: 'Barrier Failure', value: 'Inadequate isolation (LOTO)', confidence: 0.84 },
    ],
    precursorIds: ['P-002'],
  },
  {
    id: 'R1201',
    displayId: 'Report #1201',
    type: 'UNSAFE_CONDITION',
    date: '2026-08-10',
    site: 'Moran Processing Unit',
    activity: 'Confined space entry',
    hazard: 'Oxygen deficiency',
    equipment: 'Gas detector',
    barrier: 'Atmospheric monitoring gap',
    cause: 'Gas detector battery depleted mid-entry, not replaced before re-entry',
    exposure: 'Confined space entry crew',
    narrative:
      'The portable gas detector used for continuous atmospheric monitoring lost power partway through a vessel entry. Work continued for several minutes before the gap was noticed.',
    signals: [
      { label: 'Hazard', value: 'Oxygen deficiency', confidence: 0.9 },
      { label: 'Activity', value: 'Confined space entry', confidence: 0.92 },
      { label: 'Barrier Failure', value: 'Atmospheric monitoring gap', confidence: 0.88 },
    ],
    precursorIds: ['P-003'],
  },
  {
    id: 'R1218',
    displayId: 'Report #1218',
    type: 'NEAR_MISS',
    date: '2026-08-14',
    site: 'Moran Processing Unit',
    activity: 'Confined space entry',
    hazard: 'Oxygen deficiency',
    equipment: 'Ventilation blower',
    barrier: 'Atmospheric monitoring gap',
    cause: 'Forced-air ventilation not running for full duration of entry',
    exposure: 'Confined space entry crew',
    narrative:
      'A crew member noticed the ventilation blower had been switched off approximately 15 minutes into the entry, with no continuous monitoring alarm configured to catch the lapse.',
    signals: [
      { label: 'Hazard', value: 'Oxygen deficiency', confidence: 0.89 },
      { label: 'Activity', value: 'Confined space entry', confidence: 0.9 },
      { label: 'Barrier Failure', value: 'Atmospheric monitoring gap', confidence: 0.85 },
    ],
    precursorIds: ['P-003'],
  },
  {
    id: 'R1233',
    displayId: 'Report #1233',
    type: 'UNSAFE_ACT',
    date: '2026-08-18',
    site: 'Moran Processing Unit',
    activity: 'Confined space entry',
    hazard: 'Oxygen deficiency',
    equipment: 'Gas detector',
    barrier: 'Atmospheric monitoring gap',
    cause: 'Entry proceeded before initial atmospheric test was logged',
    exposure: 'Confined space entry crew',
    narrative:
      'Entry supervisor authorized entry before the initial atmospheric test reading was recorded on the permit, based on a verbal "all clear" from the previous shift.',
    signals: [
      { label: 'Hazard', value: 'Oxygen deficiency', confidence: 0.91 },
      { label: 'Activity', value: 'Confined space entry', confidence: 0.89 },
      { label: 'Barrier Failure', value: 'Atmospheric monitoring gap', confidence: 0.87 },
    ],
    precursorIds: ['P-003'],
  },
  {
    id: 'R1301',
    displayId: 'Report #1301',
    type: 'UNSAFE_CONDITION',
    date: '2026-08-20',
    site: 'Digboi Refinery Unit 2',
    activity: 'Electrical maintenance',
    hazard: 'Electric shock',
    equipment: 'Distribution panel',
    barrier: 'Inadequate lockout',
    cause: 'Panel found live despite isolation tag being present',
    exposure: 'Electrical maintenance technician',
    narrative:
      'A technician preparing to work on a distribution panel found it still energized despite an isolation tag being attached, indicating the isolation had not actually been completed.',
    signals: [
      { label: 'Hazard', value: 'Electric shock', confidence: 0.9 },
      { label: 'Activity', value: 'Electrical maintenance', confidence: 0.92 },
      { label: 'Barrier Failure', value: 'Inadequate lockout', confidence: 0.88 },
    ],
    precursorIds: ['P-004'],
  },
  {
    id: 'R1315',
    displayId: 'Report #1315',
    type: 'NEAR_MISS',
    date: '2026-08-24',
    site: 'Digboi Refinery Unit 2',
    activity: 'Electrical maintenance',
    hazard: 'Electric shock',
    equipment: 'Circuit breaker',
    barrier: 'Inadequate lockout',
    cause: 'Shared lockout point accessed by two crews without coordination',
    exposure: 'Electrical maintenance technician',
    narrative:
      'Two separate maintenance crews were found to be relying on the same lockout point without a shared lock box, creating a risk that one crew could re-energize equipment the other was working on.',
    signals: [
      { label: 'Hazard', value: 'Electric shock', confidence: 0.86 },
      { label: 'Activity', value: 'Electrical maintenance', confidence: 0.88 },
      { label: 'Barrier Failure', value: 'Inadequate lockout', confidence: 0.83 },
    ],
    precursorIds: ['P-004'],
  },
  {
    id: 'R1401',
    displayId: 'Report #1401',
    type: 'UNSAFE_CONDITION',
    date: '2026-07-10',
    site: 'Duliajan Field Site B',
    activity: 'General site movement',
    hazard: 'Slip / trip',
    equipment: 'Walkway access area',
    barrier: 'Housekeeping standard not maintained',
    cause: 'Temporary materials stored across a marked pedestrian route',
    exposure: 'Site personnel using the walkway',
    narrative:
      'Temporary materials were stored along a pedestrian walkway, reducing clear passage and creating a slip/trip exposure. The storage arrangement was scheduled for relocation.',
    signals: [
      { label: 'Hazard', value: 'Slip / trip', confidence: 0.81 },
      { label: 'Activity', value: 'General site movement', confidence: 0.78 },
      { label: 'Barrier Failure', value: 'Housekeeping standard not maintained', confidence: 0.8 },
    ],
    precursorIds: ['P-005'],
  },
  {
    id: 'R1412',
    displayId: 'Report #1412',
    type: 'NEAR_MISS',
    date: '2026-07-18',
    site: 'Duliajan Field Site B',
    activity: 'General site movement',
    hazard: 'Slip / trip',
    equipment: 'Walkway access area',
    barrier: 'Housekeeping standard not maintained',
    cause: 'Packing materials left beside the pedestrian route after maintenance work',
    exposure: 'Operators and maintenance personnel',
    narrative:
      'Packing materials were left beside a pedestrian route after maintenance work. A worker noticed the obstruction before entering the area and the materials were removed.',
    signals: [
      { label: 'Hazard', value: 'Slip / trip', confidence: 0.84 },
      { label: 'Activity', value: 'General site movement', confidence: 0.8 },
      { label: 'Barrier Failure', value: 'Housekeeping standard not maintained', confidence: 0.82 },
    ],
    precursorIds: ['P-005'],
  },
];

// ---------------------------------------------------------------------------
// Precursor patterns (cross-report groupings)
// ---------------------------------------------------------------------------

export const mockPrecursors: Precursor[] = [
  {
    id: 'P-001',
    title: 'Fall Protection Failure',
    priority: 'HIGH',
    riskScore: 85,
    status: 'OPEN',
    hazard: 'Fall from height',
    activity: 'Working at height',
    barrierFailure: 'Missing fall protection',
    site: 'Duliajan Field Site A / B',
    reportCount: 4,
    recurrenceWindowDays: 14,
    shortExplanation:
      'Four reports across two sites describe fall-protection gaps during work at height — missing anchor points, un-clipped lanyards, and a removed guardrail — within a two-week window.',
    evidence: {
      semanticSimilarity: 0.91,
      hazardMatch: true,
      activityMatch: true,
      barrierMatch: true,
      siteMatch: true,
      temporalRecurrence: 'HIGH',
      contributingReportCount: 4,
      recurrenceWindowDays: 14,
      summaryPoints: [
        'Multiple related reports (4) describe the same underlying failure mode',
        'Same hazard: fall from height',
        'Same activity: working at height',
        'Same barrier failure: missing fall protection',
        'Same site/context: Duliajan field sites',
        'Recurring within the selected time window (14 days)',
      ],
    },
    reportIds: ['R1024', 'R1088', 'R1112', 'R1140'],
    createdAt: '2026-07-30',
    updatedAt: '2026-08-04',
    reviewHistory: [],
  },
  {
    id: 'P-002',
    title: 'Isolation Verification Breakdown',
    priority: 'HIGH',
    riskScore: 78,
    status: 'OPEN',
    hazard: 'Hydrocarbon release',
    activity: 'Pipeline maintenance',
    barrierFailure: 'Inadequate isolation (LOTO)',
    site: 'Duliajan Field Site A',
    reportCount: 3,
    recurrenceWindowDays: 12,
    shortExplanation:
      'Three reports show isolation/LOTO verification steps being skipped or performed incorrectly during pipeline maintenance, suggesting a systemic gap in the isolation-check process rather than isolated errors.',
    evidence: {
      semanticSimilarity: 0.86,
      hazardMatch: true,
      activityMatch: true,
      barrierMatch: true,
      siteMatch: true,
      temporalRecurrence: 'MEDIUM',
      contributingReportCount: 3,
      recurrenceWindowDays: 12,
      summaryPoints: [
        'Multiple related reports (3) describe isolation-verification gaps',
        'Same hazard: hydrocarbon release',
        'Same activity: pipeline maintenance',
        'Same barrier failure: inadequate isolation (LOTO)',
        'Same site/context: Duliajan Field Site A',
        'Recurring within the selected time window (12 days)',
      ],
    },
    reportIds: ['R1027', 'R1055', 'R1071'],
    createdAt: '2026-07-27',
    updatedAt: '2026-08-02',
    reviewHistory: [
      {
        id: 'EV-1',
        action: 'INVESTIGATE',
        note: 'Assigned to Site HSE Officer for permit-to-work audit.',
        actor: 'HSE Reviewer (Demo)',
        timestamp: '2026-08-03',
      },
    ],
  },
  {
    id: 'P-003',
    title: 'Confined Space Atmospheric Monitoring Gap',
    priority: 'MEDIUM',
    riskScore: 64,
    status: 'UNDER_INVESTIGATION',
    hazard: 'Oxygen deficiency',
    activity: 'Confined space entry',
    barrierFailure: 'Atmospheric monitoring gap',
    site: 'Moran Processing Unit',
    reportCount: 3,
    recurrenceWindowDays: 8,
    shortExplanation:
      'Three confined-space entries at the same unit show continuous atmospheric monitoring being interrupted or skipped, indicating a possible equipment or procedural gap rather than one-off human error.',
    evidence: {
      semanticSimilarity: 0.83,
      hazardMatch: true,
      activityMatch: true,
      barrierMatch: true,
      siteMatch: true,
      temporalRecurrence: 'MEDIUM',
      contributingReportCount: 3,
      recurrenceWindowDays: 8,
      summaryPoints: [
        'Multiple related reports (3) describe monitoring interruptions',
        'Same hazard: oxygen deficiency',
        'Same activity: confined space entry',
        'Same barrier failure: atmospheric monitoring gap',
        'Same site/context: Moran Processing Unit',
        'Recurring within the selected time window (8 days)',
      ],
    },
    reportIds: ['R1201', 'R1218', 'R1233'],
    createdAt: '2026-08-14',
    updatedAt: '2026-08-19',
    reviewHistory: [
      {
        id: 'EV-2',
        action: 'INVESTIGATE',
        note: 'Ventilation equipment being inspected; monitoring SOP under review.',
        actor: 'HSE Reviewer (Demo)',
        timestamp: '2026-08-19',
      },
    ],
  },
  {
    id: 'P-004',
    title: 'Electrical Lockout Coordination Gap',
    priority: 'MEDIUM',
    riskScore: 58,
    status: 'OPEN',
    hazard: 'Electric shock',
    activity: 'Electrical maintenance',
    barrierFailure: 'Inadequate lockout',
    site: 'Digboi Refinery Unit 2',
    reportCount: 2,
    recurrenceWindowDays: 4,
    shortExplanation:
      'Two reports at the same refinery unit describe lockout points that failed to actually isolate equipment, or were shared without coordination between crews.',
    evidence: {
      semanticSimilarity: 0.79,
      hazardMatch: true,
      activityMatch: true,
      barrierMatch: true,
      siteMatch: true,
      temporalRecurrence: 'LOW',
      contributingReportCount: 2,
      recurrenceWindowDays: 4,
      summaryPoints: [
        'Related reports (2) describe lockout failures on the same unit',
        'Same hazard: electric shock',
        'Same activity: electrical maintenance',
        'Same barrier failure: inadequate lockout',
        'Same site/context: Digboi Refinery Unit 2',
      ],
    },
    reportIds: ['R1301', 'R1315'],
    createdAt: '2026-08-24',
    updatedAt: '2026-08-24',
    reviewHistory: [],
  },
  {
    id: 'P-005',
    title: 'Housekeeping Slip/Trip Cluster',
    priority: 'LOW',
    riskScore: 32,
    status: 'DISMISSED',
    hazard: 'Slip / trip',
    activity: 'General site movement',
    barrierFailure: 'Housekeeping standard not maintained',
    site: 'Duliajan Field Site B',
    reportCount: 2,
    recurrenceWindowDays: 20,
    shortExplanation:
      'Two low-severity reports of walkway obstructions were reviewed and linked to a temporary storage arrangement that has since been corrected.',
    evidence: {
      semanticSimilarity: 0.72,
      hazardMatch: true,
      activityMatch: false,
      barrierMatch: true,
      siteMatch: true,
      temporalRecurrence: 'LOW',
      contributingReportCount: 2,
      recurrenceWindowDays: 20,
      summaryPoints: [
        'Related reports (2) describe walkway obstructions',
        'Same hazard: slip / trip',
        'Same barrier failure: housekeeping standard',
        'Same site/context: Duliajan Field Site B',
      ],
    },
    reportIds: ['R1401', 'R1412'],
    createdAt: '2026-07-10',
    updatedAt: '2026-07-18',
    reviewHistory: [
      {
        id: 'EV-3',
        action: 'DISMISS',
        note: 'Temporary storage area relocated; root cause corrected. No further recurrence observed.',
        actor: 'HSE Reviewer (Demo)',
        timestamp: '2026-07-18',
      },
    ],
  },
];

// ---------------------------------------------------------------------------
// Dashboard overview
// ---------------------------------------------------------------------------

export const mockOverview: DashboardOverview = {
  reportsAnalyzed: mockReports.length,
  precursorPatternCount: mockPrecursors.length,
  highPriorityCount: mockPrecursors.filter((p) => p.priority === 'HIGH').length,
  reviewQueueCount: mockPrecursors.filter(
    (p) => p.status === 'OPEN' || p.status === 'UNDER_INVESTIGATION'
  ).length,
  lastUpdated: '2026-09-03',
};

// ---------------------------------------------------------------------------
// Relationship graph data, keyed by precursor ID
// Shape approximates a likely backend contract; see adapters.ts for
// normalization so the real API can differ from this without breaking the UI.
// ---------------------------------------------------------------------------

export const mockRelationshipGraphs: Record<string, RelationshipGraphData> = {
  'P-001': {
    nodes: [
      { id: 'R1024', type: 'report', label: 'Report #1024', sublabel: 'Jul 21' },
      { id: 'R1088', type: 'report', label: 'Report #1088', sublabel: 'Jul 25' },
      { id: 'R1112', type: 'report', label: 'Report #1112', sublabel: 'Jul 30' },
      { id: 'R1140', type: 'report', label: 'Report #1140', sublabel: 'Aug 4' },
      { id: 'P-001', type: 'precursor', label: 'Fall Protection Failure', sublabel: 'Precursor' },
    ],
    edges: [
      { id: 'e1', source: 'R1024', target: 'R1088', relationship: 'semantic_similarity', strength: 0.91, label: 'semantic similarity' },
      { id: 'e2', source: 'R1088', target: 'R1112', relationship: 'same_hazard', strength: 0.88, label: 'same hazard' },
      { id: 'e3', source: 'R1112', target: 'R1140', relationship: 'same_barrier', strength: 0.85, label: 'same barrier' },
      { id: 'e4', source: 'R1024', target: 'R1112', relationship: 'same_site', strength: 0.8, label: 'same site' },
      { id: 'e5', source: 'R1024', target: 'P-001', relationship: 'other', label: 'contributes to' },
      { id: 'e6', source: 'R1088', target: 'P-001', relationship: 'other', label: 'contributes to' },
      { id: 'e7', source: 'R1112', target: 'P-001', relationship: 'other', label: 'contributes to' },
      { id: 'e8', source: 'R1140', target: 'P-001', relationship: 'other', label: 'contributes to' },
    ],
  },
  'P-002': {
    nodes: [
      { id: 'R1027', type: 'report', label: 'Report #1027', sublabel: 'Jul 22' },
      { id: 'R1055', type: 'report', label: 'Report #1055', sublabel: 'Jul 27' },
      { id: 'R1071', type: 'report', label: 'Report #1071', sublabel: 'Aug 2' },
      { id: 'P-002', type: 'precursor', label: 'Isolation Verification Breakdown', sublabel: 'Precursor' },
    ],
    edges: [
      { id: 'e1', source: 'R1027', target: 'R1055', relationship: 'same_barrier', strength: 0.86, label: 'same barrier' },
      { id: 'e2', source: 'R1055', target: 'R1071', relationship: 'semantic_similarity', strength: 0.84, label: 'semantic similarity' },
      { id: 'e3', source: 'R1027', target: 'R1071', relationship: 'same_activity', strength: 0.82, label: 'same activity' },
      { id: 'e4', source: 'R1027', target: 'P-002', relationship: 'other', label: 'contributes to' },
      { id: 'e5', source: 'R1055', target: 'P-002', relationship: 'other', label: 'contributes to' },
      { id: 'e6', source: 'R1071', target: 'P-002', relationship: 'other', label: 'contributes to' },
    ],
  },
  'P-003': {
    nodes: [
      { id: 'R1201', type: 'report', label: 'Report #1201', sublabel: 'Aug 10' },
      { id: 'R1218', type: 'report', label: 'Report #1218', sublabel: 'Aug 14' },
      { id: 'R1233', type: 'report', label: 'Report #1233', sublabel: 'Aug 18' },
      { id: 'P-003', type: 'precursor', label: 'Atmospheric Monitoring Gap', sublabel: 'Precursor' },
    ],
    edges: [
      { id: 'e1', source: 'R1201', target: 'R1218', relationship: 'same_barrier', strength: 0.85, label: 'same barrier' },
      { id: 'e2', source: 'R1218', target: 'R1233', relationship: 'same_hazard', strength: 0.83, label: 'same hazard' },
      { id: 'e3', source: 'R1201', target: 'R1233', relationship: 'same_site', strength: 0.81, label: 'same site' },
      { id: 'e4', source: 'R1201', target: 'P-003', relationship: 'other', label: 'contributes to' },
      { id: 'e5', source: 'R1218', target: 'P-003', relationship: 'other', label: 'contributes to' },
      { id: 'e6', source: 'R1233', target: 'P-003', relationship: 'other', label: 'contributes to' },
    ],
  },
  'P-004': {
    nodes: [
      { id: 'R1301', type: 'report', label: 'Report #1301', sublabel: 'Aug 20' },
      { id: 'R1315', type: 'report', label: 'Report #1315', sublabel: 'Aug 24' },
      { id: 'P-004', type: 'precursor', label: 'Electrical Lockout Gap', sublabel: 'Precursor' },
    ],
    edges: [
      { id: 'e1', source: 'R1301', target: 'R1315', relationship: 'same_barrier', strength: 0.79, label: 'same barrier' },
      { id: 'e2', source: 'R1301', target: 'P-004', relationship: 'other', label: 'contributes to' },
      { id: 'e3', source: 'R1315', target: 'P-004', relationship: 'other', label: 'contributes to' },
    ],
  },
  'P-005': {
    nodes: [
      { id: 'R1401', type: 'report', label: 'Report #1401', sublabel: 'Jul 10' },
      { id: 'R1412', type: 'report', label: 'Report #1412', sublabel: 'Jul 18' },
      { id: 'P-005', type: 'precursor', label: 'Housekeeping Slip/Trip Cluster', sublabel: 'Precursor (Dismissed)' },
    ],
    edges: [
      { id: 'P5-E1', source: 'R1401', target: 'R1412', relationship: 'temporal_recurrence', strength: 0.78 },
      { id: 'P5-E2', source: 'R1401', target: 'P-005', relationship: 'same_hazard', strength: 0.81 },
      { id: 'P5-E3', source: 'R1412', target: 'P-005', relationship: 'same_barrier', strength: 0.82 },
    ],
  },
};
