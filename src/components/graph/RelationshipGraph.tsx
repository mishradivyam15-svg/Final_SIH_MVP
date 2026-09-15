import { useCallback, useMemo, useState, type CSSProperties } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  type Edge,
  type Node,
  Position,
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { RelationshipGraphData } from '@/types';
import { EmptyState } from '@/components/common/EmptyState';
import { RELATIONSHIP_COLOR, RELATIONSHIP_LABEL } from '@/lib/display';
import { Network } from 'lucide-react';

interface RelationshipGraphProps {
  data: RelationshipGraphData;
}

/**
 * Fully data-driven: nodes/edges come from the normalized graph model
 * (see src/services/adapters.ts). No relationship is hard-coded here —
 * layout is computed from whatever the API/mock service returns.
 */
export function RelationshipGraph({ data }: RelationshipGraphProps) {
  const { nodes, edges } = data;
  const navigate = useNavigate();
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const precursorId = useMemo(
    () => nodes.find((n) => n.type === 'precursor')?.id,
    [nodes]
  );

  // Deliberately NOT dependent on hover state: this component has no
  // onNodesChange handler, so re-creating the nodes array would snap any
  // node the user has dragged back to its computed position. Node hover
  // styling is handled in CSS instead.
  const flowNodes: Node[] = useMemo(() => {
    const reportNodes = nodes.filter((n) => n.type === 'report');
    const precursorNode = nodes.find((n) => n.type === 'precursor');

    const radius = Math.min(180, 95 + reportNodes.length * 16);
    const centerX = 270;
    const centerY = 170;

    const positioned: Node[] = reportNodes.map((n, i) => {
      const angle = (2 * Math.PI * i) / Math.max(reportNodes.length, 1) - Math.PI / 2;
      return {
        id: n.id,
        position: {
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        },
        data: { label: <NodeCard type="report" label={n.label} sublabel={n.sublabel} /> },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        style: nodeShell(130),
        draggable: true,
      };
    });

    if (precursorNode) {
      positioned.push({
        id: precursorNode.id,
        position: { x: centerX, y: centerY },
        data: {
          label: (
            <NodeCard
              type="precursor"
              label={precursorNode.label}
              sublabel={precursorNode.sublabel}
            />
          ),
        },
        style: nodeShell(170),
      });
    }

    return positioned;
  }, [nodes]);

  // Edges re-derive on hover so the hovered node's connections light up and
  // the rest recede. Safe to rebuild — edges are never user-edited.
  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => {
        const color = RELATIONSHIP_COLOR[e.relationship];
        const isStructural = e.relationship === 'other';
        const isConnected = !hoveredId || e.source === hoveredId || e.target === hoveredId;
        const baseWidth = e.strength ? 1 + e.strength * 2 : 1.5;

        const opacity = !isConnected ? 0.08 : isStructural ? 0.4 : 0.95;

        return {
          id: e.id,
          source: e.source,
          target: e.target,
          label: isStructural || !isConnected ? undefined : e.label || RELATIONSHIP_LABEL[e.relationship],
          // Flowing dashes show the direction a relationship was inferred in.
          animated: isConnected && !isStructural,
          style: {
            stroke: color,
            strokeWidth: hoveredId && isConnected ? baseWidth + 1.2 : baseWidth,
            opacity,
            transition: 'opacity 250ms ease, stroke-width 250ms ease',
            filter: hoveredId && isConnected ? `drop-shadow(0 0 5px ${color})` : undefined,
          },
          labelStyle: { fontSize: 10, fill: '#eef1f5', fontWeight: 600 },
          labelBgStyle: { fill: '#151a23', fillOpacity: 0.92 },
          markerEnd: isStructural
            ? undefined
            : { type: MarkerType.ArrowClosed, color, width: 14, height: 14 },
        };
      }),
    [edges, hoveredId]
  );

  const onNodeMouseEnter = useCallback((_: unknown, node: Node) => setHoveredId(node.id), []);
  const onNodeMouseLeave = useCallback(() => setHoveredId(null), []);

  if (nodes.length === 0) {
    return (
      <EmptyState
        icon={Network}
        title="Relationship data is not available for this precursor"
        description="The relationship graph will populate once the AI/ML relationship engine supplies data for this pattern."
      />
    );
  }

  const relationshipTypesUsed = Array.from(new Set(edges.map((e) => e.relationship))).filter(
    (r) => r !== 'other'
  );

  const connectionCount = hoveredId
    ? edges.filter(
        (e) => (e.source === hoveredId || e.target === hoveredId) && e.relationship !== 'other'
      ).length
    : 0;

  return (
    <div className="rounded-xl panel-sheen border border-ink-300/40 bg-surface p-4 shadow-card">
      <div className="mb-3 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-semibold text-ink-900">Relationship Graph</h2>
          <p className="mt-0.5 text-[11px] text-ink-400">
            {hoveredId
              ? `${connectionCount} relationship${connectionCount === 1 ? '' : 's'} on this node`
              : 'Hover a node to trace its links · click a report to open it.'}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          {relationshipTypesUsed.map((r) => (
            <span key={r} className="flex items-center gap-1.5 text-[11px] text-ink-500">
              <span
                className="h-2 w-2 rounded-full"
                style={{
                  backgroundColor: RELATIONSHIP_COLOR[r],
                  boxShadow: `0 0 6px -1px ${RELATIONSHIP_COLOR[r]}`,
                }}
                aria-hidden="true"
              />
              {RELATIONSHIP_LABEL[r]}
            </span>
          ))}
        </div>
      </div>
      <div style={{ height: 340 }} className="overflow-hidden rounded-md border border-ink-300/30">
        <ReactFlow
          nodes={flowNodes}
          edges={flowEdges}
          onNodeClick={(_, node) => {
            if (node.id !== precursorId) navigate(`/reports/${node.id}`);
          }}
          onNodeMouseEnter={onNodeMouseEnter}
          onNodeMouseLeave={onNodeMouseLeave}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#2a313d" gap={18} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}

/**
 * The visual card lives inside the node rather than on it: ReactFlow owns
 * the transform on `.react-flow__node` for positioning, so anything that
 * scales has to be a child or it fights the layout.
 */
function NodeCard({
  type,
  label,
  sublabel,
}: {
  type: 'report' | 'precursor';
  label: string;
  sublabel?: string;
}) {
  return (
    <div className={`graph-node-card graph-node-card--${type}`}>
      <div className="text-xs font-semibold">{label}</div>
      {sublabel && <div className="text-[10px] opacity-75">{sublabel}</div>}
    </div>
  );
}

/** Strips ReactFlow's default node chrome so NodeCard can own the styling. */
function nodeShell(width: number): CSSProperties {
  return {
    width,
    background: 'transparent',
    border: 'none',
    padding: 0,
    borderRadius: 0,
    boxShadow: 'none',
  };
}
