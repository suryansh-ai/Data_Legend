import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Database, BarChart3, CheckCircle2, AlertCircle } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { api } from '@/lib/api'
import LoadingSpinner from '@/components/LoadingSpinner'
import type { FacilityStats, TrustResult } from '@/lib/types'
import { formatNumber, trustLabel } from '@/lib/utils'

const FIELD_LABELS: Record<string, string> = {
  name: 'Name',
  description: 'Description',
  capability: 'Capability',
  procedure: 'Procedure',
  equipment: 'Equipment',
  specialties: 'Specialties',
  numberDoctors: 'Doctors',
  capacity: 'Capacity',
  address_stateOrRegion: 'State',
  address_city: 'City',
  latitude: 'Latitude',
  longitude: 'Longitude',
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

  const trustPieData = Object.entries(trustDist).map(([signal, count]) => ({
    name: trustLabel(signal),
    value: count,
    color: SIGNAL_COLORS[signal] || '#6b7280',
  }))

  const avgCompleteness = completenessData.reduce((s, d) => s + d.completeness, 0) / (completenessData.length || 1)
  const fieldsAbove80 = completenessData.filter(d => d.completeness >= 80).length
  const fieldsBelow50 = completenessData.filter(d => d.completeness < 50).length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          <Database className="mr-2 inline h-6 w-6 text-violet-500" />
          Data Readiness
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          Audit data quality, completeness, and trust distribution across all facility records
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card">
          <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{formatNumber(stats?.total ?? 0)}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Total Records</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="card">
          <p className="text-2xl font-bold text-brand-600">{avgCompleteness.toFixed(1)}%</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Avg Completeness</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="card">
          <p className="text-2xl font-bold text-emerald-500">{fieldsAbove80}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Fields &gt; 80%</p>
        </motion.div>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="card">
          <p className="text-2xl font-bold text-red-500">{fieldsBelow50}</p>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>Fields &lt; 50%</p>
        </motion.div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Column Completeness */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card">
          <h2 className="mb-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
            <BarChart3 className="mr-2 inline h-5 w-5 text-brand-500" />
            Column Completeness
          </h2>
          <div className="space-y-3">
            {completenessData.map(({ field, completeness, count }) => (
              <div key={field}>
                <div className="flex items-center justify-between text-sm">
                  <span style={{ color: 'var(--text-primary)' }}>{field}</span>
                  <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                    {count.toLocaleString('en-IN')} / {totalRows.toLocaleString('en-IN')} ({completeness.toFixed(1)}%)
                  </span>
                </div>
                <div className="mt-1 h-2 overflow-hidden rounded-full" style={{ backgroundColor: 'var(--bg-tertiary)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${completeness}%` }}
                    transition={{ duration: 0.8, delay: 0.1 }}
                    className="h-full rounded-full"
                    style={{
                      backgroundColor: completeness >= 80 ? '#10b981' :
                        completeness >= 50 ? '#f59e0b' : '#ef4444',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Trust Distribution */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card">
          <h2 className="mb-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
            Trust Signal Distribution
          </h2>
          {trustPieData.length > 0 ? (
            <div className="flex items-center gap-6">
              <ResponsiveContainer width="50%" height={200}>
                <PieChart>
                  <Pie
                    data={trustPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {trustPieData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      fontSize: '12px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2">
                {trustPieData.map(d => (
                  <div key={d.name} className="flex items-center gap-2 text-sm">
                    <div className="h-3 w-3 rounded-full" style={{ backgroundColor: d.color }} />
                    <span style={{ color: 'var(--text-primary)' }}>{d.name}</span>
                    <span className="font-mono text-xs" style={{ color: 'var(--text-muted)' }}>
                      {d.value.toLocaleString('en-IN')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>No trust distribution data available</p>
          )}

          {/* Issues */}
          <div className="mt-6">
            <h3 className="mb-2 text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
              Data Quality Issues
            </h3>
            <div className="space-y-2">
              {completenessData
                .filter(d => d.completeness < 50)
                .map(d => (
                  <div key={d.field} className="flex items-start gap-2 text-sm">
                    <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-amber-500" />
                    <span style={{ color: 'var(--text-secondary)' }}>
                      <strong>{d.field}</strong> has only {d.completeness.toFixed(1)}% completeness — 
                      {d.count.toLocaleString('en-IN')} of {totalRows.toLocaleString('en-IN')} records populated
                    </span>
                  </div>
                ))}
              {completenessData.filter(d => d.completeness < 50).length === 0 && (
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                  <span style={{ color: 'var(--text-secondary)' }}>All fields have &gt; 50% completeness</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Completeness Bar Chart */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="card">
        <h2 className="mb-4 font-semibold" style={{ color: 'var(--text-primary)' }}>
          Field Completeness Overview
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={completenessData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <XAxis dataKey="field" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} />
            <YAxis tick={{ fontSize: 11, fill: 'var(--text-muted)' }} domain={[0, 100]} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="completeness" radius={[4, 4, 0, 0]}>
              {completenessData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.completeness >= 80 ? '#10b981' : entry.completeness >= 50 ? '#f59e0b' : '#ef4444'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </motion.div>
    </div>
  )
}
