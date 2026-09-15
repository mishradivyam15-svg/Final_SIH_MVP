import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { Precursor } from '@/types';

interface PriorityDistributionChartProps {
  precursors: Precursor[];
}

const COLORS: Record<string, string> = {
  High: '#f87171',
  Medium: '#fbbf24',
  Low: '#4ade80',
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
    <div className="animate-fade-in-up rounded-xl panel-sheen border border-ink-300/40 bg-surface p-4 shadow-card">
      <h3 className="mb-3 text-sm font-semibold tracking-tight text-ink-900">Patterns by Priority</h3>
      <ResponsiveContainer width="100%" height={172}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 28 }} barCategoryGap={14}>
          <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#242b36" />
          <XAxis
            type="number"
            allowDecimals={false}
            tick={{ fontSize: 11, fill: '#8a93a1', fontFamily: 'JetBrains Mono' }}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fontSize: 12, fill: '#b7c0cc', fontWeight: 500 }}
            width={56}
          />
          <Tooltip
            cursor={{ fill: '#1e2530' }}
            contentStyle={{
              fontSize: 12,
              borderRadius: 10,
              borderColor: '#2a313d',
              backgroundColor: '#151a23',
              color: '#eef1f5',
              boxShadow: '0 8px 24px -6px rgba(0,0,0,0.5)',
            }}
          />
          <Bar
            dataKey="count"
            radius={[0, 6, 6, 0]}
            barSize={26}
            isAnimationActive
            animationDuration={700}
            animationEasing="ease-out"
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
