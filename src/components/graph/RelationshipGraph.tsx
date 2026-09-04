import { useMemo, type CSSProperties } from 'react';
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
        data: { label: <NodeLabel label={n.label} sublabel={n.sublabel} /> },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
        style: nodeStyle('report'),
        draggable: true,
      };
    });

    if (precursorNode) {
      positioned.push({
        id: precursorNode.id,
        position: { x: centerX, y: centerY },
        data: { label: <NodeLabel label={precursorNode.label} sublabel={precursorNode.sublabel} /> },
        style: nodeStyle('precursor'),
      });
    }

    return positioned;
  }, [nodes]);

  const flowEdges: Edge[] = useMemo(
    () =>
      edges.map((e) => {
        const color = RELATIONSHIP_COLOR[e.relationship];
        const isStructural = e.relationship === 'other';
        return {
          id: e.id,
          source: e.source,
          target: e.target,
          label: isStructural ? undefined : e.label || RELATIONSHIP_LABEL[e.relationship],
          animated: false,
          style: {
            stroke: color,
            strokeWidth: e.strength ? 1 + e.strength * 2 : 1.5,
            opacity: isStructural ? 0.35 : 0.9,
          },
          labelStyle: { fontSize: 10, fill: '#333944', fontWeight: 600 },
          labelBgStyle: { fill: '#ffffff', fillOpacity: 0.9 },
          markerEnd: isStructural
            ? undefined
            : { type: MarkerType.ArrowClosed, color, width: 14, height: 14 },
        };
      }),
    [edges]
  );

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

  return (
    <div className="rounded-lg border border-ink-300/40 bg-white p-4 shadow-card">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-ink-900">Relationship Graph</h2>
          <p className="mt-0.5 text-[11px] text-ink-400">Click a report node to inspect its source report.</p>
        </div>
        <div className="flex flex-wrap gap-3">
          {relationshipTypesUsed.map((r) => (
            <span key={r} className="flex items-center gap-1.5 text-[11px] text-ink-500">
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: RELATIONSHIP_COLOR[r] }}
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
            if (node.id !== data.nodes.find((n) => n.type === 'precursor')?.id) {
              navigate(`/reports/${node.id}`);
            }
          }}
          fitView
          fitViewOptions={{ padding: 0.3 }}
          nodesDraggable
          nodesConnectable={false}
          elementsSelectable
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#eef0f3" gap={18} />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>
    </div>
  );
}

function NodeLabel({ label, sublabel }: { label: string; sublabel?: string }) {
  return (
    <div className="text-center">
      <div className="text-xs font-semibold">{label}</div>
      {sublabel && <div className="text-[10px] opacity-75">{sublabel}</div>}
    </div>
  );
}

function nodeStyle(type: 'report' | 'precursor'): CSSProperties {
  if (type === 'precursor') {
    return {
      background: '#b3261e',
      color: 'white',
      border: '2px solid #8f1d17',
      borderRadius: 10,
      padding: '8px 12px',
      width: 170,
      fontWeight: 600,
    };
  }
  return {
    background: '#ffffff',
    color: '#12161c',
    border: '1.5px solid #b3cce9',
    borderRadius: 8,
    padding: '6px 10px',
    width: 130,
  };
}
