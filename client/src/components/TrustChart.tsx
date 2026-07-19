import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'
import type { TrustResult } from '@/lib/types'
import { trustScoreColor } from '@/lib/utils'

interface TrustChartProps {
  trust: TrustResult
  variant?: 'radar' | 'bar'
}

const SIGNAL_COLORS: Record<string, string> = {
  CORROBORATED: '#10b981',
  CLAIMED_ONLY: '#f59e0b',
  WEAK: '#ef4444',
  UNKNOWN: '#6b7280',
}

export default function TrustChart({ trust, variant = 'radar' }: TrustChartProps) {
  const capData = Object.entries(trust.capabilities).map(([name, cap]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    score: cap.score * 100,
    signal: cap.signal,
  }))

  if (variant === 'bar') {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={capData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <XAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
          <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
          <Bar dataKey="score" radius={[4, 4, 0, 0]}>
            {capData.map((entry, i) => (
              <Cell key={i} fill={SIGNAL_COLORS[entry.signal] || '#6b7280'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={capData}>
        <PolarGrid stroke="var(--border-color)" />
        <PolarAngleAxis dataKey="name" tick={{ fontSize: 11, fill: 'var(--text-secondary)' }} />
        <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10, fill: 'var(--text-muted)' }} />
        <Radar
          name="Trust Score"
          dataKey="score"
          stroke={trustScoreColor(trust.overall_trust)}
          fill={trustScoreColor(trust.overall_trust)}
          fillOpacity={0.2}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
