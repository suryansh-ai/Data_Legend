import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Database, CheckCircle, AlertTriangle, AlertCircle, Info, Sparkles, TrendingUp } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { api } from '@/lib/api'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { FacilityStats } from '@/lib/types'
import { formatNumber, trustLabel } from '@/lib/utils'

const FIELD_LABELS: Record<string, string> = {
  name: 'Hospital Name',
  description: 'Unstructured Description',
  capability: 'Stated Capabilities',
  procedure: 'Procedure Logs',
  equipment: 'Equipment Inventory',
  specialties: 'Clinical Specialties',
  numberDoctors: 'Doctors Count',
  capacity: 'Bed Capacity',
  address_stateOrRegion: 'State Name',
  address_city: 'City Name',
  latitude: 'Latitude Coordinate',
  longitude: 'Longitude Coordinate',
}

const SIGNAL_COLORS: Record<string, string> = {
  CORROBORATED: '#10b981',
  CLAIMED_ONLY: '#f59e0b',
  WEAK: '#ef4444',
  UNKNOWN: '#6b7280',
}

export default function DataReadiness() {
  const [stats, setStats] = useState<FacilityStats | null>(null)
  const [completeness, setCompleteness] = useState<Record<string, number>>({})
  const [trustDist, setTrustDist] = useState<Record<string, number>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getColumnCompleteness(), api.getTrustDistribution()])
      .then(([s, c, t]) => { setStats(s); setCompleteness(c); setTrustDist(t) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner />

  const totalRows = stats?.total ?? 1
  const completenessData = Object.entries(completeness)
    .map(([field, count]) => ({
      field: FIELD_LABELS[field] || field,
      completeness: (count / totalRows) * 100,
      count,
    }))
    .sort((a, b) => b.completeness - a.completeness)

  const avgCompleteness = completenessData.reduce((s, d) => s + d.completeness, 0) / (completenessData.length || 1)
  const fieldsAbove80 = completenessData.filter(d => d.completeness >= 80).length
  const fieldsBelow50 = completenessData.filter(d => d.completeness < 50).length

  return (
    <div className="space-y-8 py-2">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight" style={{ color: 'var(--text-primary)' }}>
          Data Readiness & Quality
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Audit completeness indicators, missing values, and corroboration distribution.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block" style={{ color: 'var(--text-primary)' }}>
            {formatNumber(stats?.total ?? 0)}
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Total Records</span>
          <span className="text-[10px] text-slate-400 block">All registry hospital rows</span>
        </div>

        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block text-teal-700 dark:text-teal-400">
            {avgCompleteness.toFixed(1)}%
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Avg Completeness</span>
          <span className="text-[10px] text-slate-400 block">Overall data populate ratio</span>
        </div>

        <div className="card p-5 space-y-1">
          <span className="text-2xl font-black block text-emerald-600">
            {fieldsAbove80}
          </span>
          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Healthy Fields</span>
          <span className="text-[10px] text-slate-400 block">Completeness above 80%</span>
        </div>

        <div className="card p-5 space-y-1 border-red-200 bg-red-50/20">
          <span className="text-2xl font-black block text-red-600">
            {fieldsBelow50}
          </span>
          <span className="text-xs font-bold text-red-800 dark:text-red-400 block">Sparse Fields</span>
          <span className="text-[10px] text-red-500 block">Fields with missing values</span>
        </div>
      </div>

      {/* Main Layout Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Column Completeness Progress Bars */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="card p-6 space-y-4">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
              📋 Field Fill Summary
            </h2>
            <p className="text-[10px] text-slate-400">What proportion of details are filled in our hospital database.</p>
          </div>

          <div className="space-y-3.5">
            {completenessData.map(({ field, completeness, count }) => (
              <div key={field} className="space-y-1">
                <div className="flex items-center justify-between text-xs font-bold">
                  <span style={{ color: 'var(--text-primary)' }}>{field}</span>
                  <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                    {count.toLocaleString('en-IN')} / {totalRows.toLocaleString('en-IN')} ({completeness.toFixed(0)}%)
                  </span>
                </div>
                <div className="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${completeness}%`,
                      backgroundColor: completeness >= 80 ? 'var(--success)' :
                        completeness >= 50 ? 'var(--warning)' : 'var(--danger)',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        <div className="space-y-6">
          {/* Trust Distribution */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card p-6 space-y-4">
            <div>
              <h2 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
                🛡️ Verification Distribution
              </h2>
              <p className="text-[10px] text-slate-400">How many clinics fit each trust category.</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {Object.entries(trustDist).map(([signal, count]) => {
                const color = SIGNAL_COLORS[signal] || '#6b7280';
                return (
                  <div key={signal} className="p-3.5 rounded-xl border bg-slate-50 dark:bg-slate-900 flex justify-between items-center" style={{ borderColor: 'var(--border-color)' }}>
                    <div>
                      <span className="text-xs font-bold block" style={{ color: 'var(--text-primary)' }}>{trustLabel(signal)}</span>
                      <span className="text-[9px] block text-slate-400 font-semibold uppercase tracking-wider mt-0.5">Category</span>
                    </div>
                    <span className="text-base font-extrabold" style={{ color }}>{count.toLocaleString('en-IN')}</span>
                  </div>
                );
              })}
            </div>
          </motion.div>

          {/* Quality warnings */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
              <AlertTriangle className="h-4.5 w-4.5 text-amber-500" />
              Critical Data Action Items
            </h3>
            <div className="space-y-3">
              {completenessData
                .filter(d => d.completeness < 50)
                .map(d => (
                  <div key={d.field} className="p-3.5 rounded-xl border border-amber-200/50 bg-amber-50/20 text-xs flex items-start gap-2.5">
                    <AlertCircle className="h-4.5 w-4.5 text-amber-600 shrink-0" />
                    <div>
                      <h4 className="font-extrabold text-amber-900 dark:text-amber-400">{d.field} needs population</h4>
                      <p className="text-[10px] text-slate-500 leading-relaxed mt-0.5">
                        Only {d.completeness.toFixed(0)}% filled ({d.count.toLocaleString('en-IN')} locations). Lack of this data makes matching difficult.
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Field Completeness Chart */}
      <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card p-6 space-y-4">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--text-primary)' }}>
            📊 Dataset Completeness Audit
          </h2>
          <p className="text-[10px] text-slate-400">Visual comparison of database columns completeness level.</p>
        </div>

        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={completenessData} margin={{ top: 5, right: 10, bottom: 5, left: -20 }}>
              <XAxis dataKey="field" tick={{ fontSize: 9, fill: 'var(--text-muted)' }} />
              <YAxis tick={{ fontSize: 9, fill: 'var(--text-muted)' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-primary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  fontSize: '11px',
                }}
              />
              <Bar dataKey="completeness" radius={[4, 4, 0, 0]}>
                {completenessData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.completeness >= 80 ? '#0f766e' : entry.completeness >= 50 ? '#d97706' : '#b91c1c'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </div>
  )
}
