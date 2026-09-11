import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { Precursor } from '@/types';

interface PriorityDistributionChartProps {
  precursors: Precursor[];
}

const COLORS: Record<string, string> = {
  High: '#b3261e',
  Medium: '#8a5a00',
  Low: '#1f6f4a',
};

/**
 * The single chart in the app: precursor count by priority.
 * Kept intentionally minimal — it supports the evidence story
 * ("how many recurring patterns are severe") rather than decorating the page.
 */
export function PriorityDistributionChart({ precursors }: PriorityDistributionChartProps) {
  const data = [
    { name: 'High', count: precursors.filter((p) => p.priority === 'HIGH').length },
    { name: 'Medium', count: precursors.filter((p) => p.priority === 'MEDIUM').length },
    { name: 'Low', count: precursors.filter((p) => p.priority === 'LOW').length },
  ];

  return (
    <div className="rounded-lg border border-ink-300/40 bg-white p-4 shadow-card">
      <h3 className="mb-3 text-sm font-semibold text-ink-900">Patterns by Priority</h3>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#eef0f3" />
          <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11, fill: '#7c8593' }} />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: '#333944' }}
            width={56}
          />
          <Tooltip
            cursor={{ fill: '#f7f8fa' }}
            contentStyle={{ fontSize: 12, borderRadius: 8, borderColor: '#eef0f3' }}
          />
          <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={22}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
